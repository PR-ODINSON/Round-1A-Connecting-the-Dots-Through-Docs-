import { Injectable, InternalServerErrorException, Logger, BadRequestException } from '@nestjs/common';
import axios, { AxiosError } from 'axios';
import { DocumentStructureDto, HeadingDto } from './dto/document-structure.dto';

@Injectable()
export class PdfExtractionService {
  private readonly logger = new Logger(PdfExtractionService.name);
  private readonly pythonServiceUrl: string;

  constructor() {
    // Docker service name or localhost for development
    this.pythonServiceUrl = process.env.PYTHON_SERVICE_URL || 'http://python-parser:8000';
    this.logger.log(`Initialized with Python service URL: ${this.pythonServiceUrl}`);
  }

  async extractStructure(file: Express.Multer.File): Promise<DocumentStructureDto> {
    const startTime = Date.now();
    
    try {
      // Additional file validation
      this.validatePdfFile(file);

      // Create form data to send to Python microservice
      const FormData = require('form-data');
      const formData = new FormData();
      formData.append('file', file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });

      this.logger.log(`🐍 Sending PDF to Python service: ${this.pythonServiceUrl}/extract-headings`);
      this.logger.debug(`File details: ${file.originalname} (${file.size} bytes)`);
      
      // Call Python microservice with proper timeout and retry logic
      const response = await this.callPythonService(formData);
      const pythonResult = response.data;
      
      // Validate and transform the response
      this.validatePythonResponse(pythonResult);

      // Transform Python response to our DTO format
      const documentStructure = this.transformResponseToDto(pythonResult, file.originalname);
      
      const processingTime = Date.now() - startTime;
      this.logger.log(`✅ Successfully processed PDF: ${documentStructure.title} | ${documentStructure.outline.length} headings | ${processingTime}ms`);
      
      return documentStructure;
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.logger.error(`❌ Error processing PDF ${file.originalname} after ${processingTime}ms:`, error);
      
      if (error instanceof BadRequestException || error instanceof InternalServerErrorException) {
        throw error;
      }
      
      throw new InternalServerErrorException(
        `Failed to extract PDF structure: ${error.message}`,
      );
    }
  }

  private validatePdfFile(file: Express.Multer.File): void {
    if (!file.buffer || file.buffer.length === 0) {
      throw new BadRequestException('File is empty or corrupted');
    }

    // Check PDF magic bytes
    const pdfMagic = file.buffer.slice(0, 4).toString();
    if (!pdfMagic.includes('%PDF')) {
      throw new BadRequestException('File does not appear to be a valid PDF');
    }

    // Additional size validation
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      throw new BadRequestException(
        `File too large: ${(file.size / (1024*1024)).toFixed(1)}MB. Maximum allowed: 50MB`
      );
    }
  }

  private async callPythonService(formData: any): Promise<any> {
    const maxRetries = 3;
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        this.logger.debug(`Python service call attempt ${attempt}/${maxRetries}`);
        
        const response = await axios.post(
          `${this.pythonServiceUrl}/extract-headings`,
          formData,
          {
            headers: {
              ...formData.getHeaders(),
              'Accept': 'application/json',
            },
            timeout: 120000, // 2 minutes timeout for large PDFs
            maxBodyLength: 100 * 1024 * 1024, // 100MB max request size
            maxContentLength: 100 * 1024 * 1024,
          },
        );

        return response;
        
      } catch (error) {
        lastError = error;
        this.logger.warn(`Python service call attempt ${attempt} failed:`, error.message);
        
        if (attempt < maxRetries && this.isRetryableError(error)) {
          // Wait before retry (exponential backoff)
          const delay = Math.pow(2, attempt) * 1000;
          this.logger.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
        
        // Transform axios errors to appropriate exceptions
        if (axios.isAxiosError(error)) {
          throw this.handleAxiosError(error);
        }
        
        throw error;
      }
    }

    throw lastError;
  }

  private isRetryableError(error: any): boolean {
    if (axios.isAxiosError(error)) {
      // Retry on network errors or 5xx server errors
      return !error.response || (error.response.status >= 500 && error.response.status < 600);
    }
    return false;
  }

  private handleAxiosError(error: AxiosError): Error {
    const status = error.response?.status;
    const message = (error.response?.data as any)?.detail || error.message;
    
    if (status === 400) {
      return new BadRequestException(`Invalid PDF: ${message}`);
    } else if (status === 413) {
      return new BadRequestException('PDF file too large for processing');
    } else if (status === 422) {
      return new BadRequestException(`PDF processing error: ${message}`);
    } else if (status >= 500) {
      return new InternalServerErrorException(`Python service error: ${message}`);
    } else if (error.code === 'ECONNREFUSED') {
      return new InternalServerErrorException('Python service is not reachable. Please ensure the service is running.');
    } else if (error.code === 'ETIMEDOUT') {
      return new InternalServerErrorException('PDF processing timed out. The document may be too complex or large.');
    }
    
    return new InternalServerErrorException(`Unexpected error: ${message}`);
  }

  private validatePythonResponse(pythonResult: any): void {
    if (!pythonResult || typeof pythonResult !== 'object') {
      throw new InternalServerErrorException('Invalid response from Python service');
    }

    if (!pythonResult.title && !pythonResult.outline) {
      throw new InternalServerErrorException('Python service returned incomplete data');
    }

    // Validate outline structure
    if (pythonResult.outline && !Array.isArray(pythonResult.outline)) {
      throw new InternalServerErrorException('Invalid outline data from Python service');
    }
  }

  private transformResponseToDto(pythonResult: any, originalFilename: string): DocumentStructureDto {
    // Transform Python response to our DTO format
    const documentStructure: DocumentStructureDto = {
      title: pythonResult.title || this.extractTitleFromFilename(originalFilename),
      outline: (pythonResult.outline || []).map((heading: any): HeadingDto => ({
        level: this.validateHeadingLevel(heading.level),
        text: String(heading.text || '').trim(),
        page: Math.max(1, parseInt(heading.page) || 1),
      })).filter((heading: HeadingDto) => heading.text.length > 0),
      metadata: {
        totalPages: Math.max(0, parseInt(pythonResult.metadata?.total_pages) || 0),
        processingTimeMs: Math.max(0, parseFloat(pythonResult.metadata?.processing_time_ms) || 0),
        fontMetrics: this.formatFontMetrics(pythonResult.metadata?.font_metrics || {}),
      },
    };

    return documentStructure;
  }

  private validateHeadingLevel(level: any): 'H1' | 'H2' | 'H3' {
    const validLevels = ['H1', 'H2', 'H3'];
    const levelStr = String(level || '').toUpperCase();
    return validLevels.includes(levelStr) ? levelStr as 'H1' | 'H2' | 'H3' : 'H1';
  }

  private formatFontMetrics(fontMetrics: any): Record<string, any> {
    if (!fontMetrics || typeof fontMetrics !== 'object') {
      return {};
    }

    const formatted: Record<string, any> = {};
    
    for (const [fontName, metrics] of Object.entries(fontMetrics)) {
      if (metrics && typeof metrics === 'object') {
        formatted[fontName] = {
          avg_size: Math.round((metrics as any).avg_size * 10) / 10 || 0,
          max_size: Math.round((metrics as any).max_size * 10) / 10 || 0,
          min_size: Math.round((metrics as any).min_size * 10) / 10 || 0,
          count: Math.max(0, parseInt((metrics as any).count) || 0),
        };
      }
    }

    return formatted;
  }

  private extractTitleFromFilename(filename: string): string {
    if (!filename) {
      return 'Untitled Document';
    }

    // Remove extension and clean up
    let title = filename.replace(/\.[^/.]+$/, '');
    title = title.replace(/[_-]/g, ' ');
    title = title.replace(/\s+/g, ' ').trim();
    
    // Capitalize first letter of each word
    title = title.replace(/\b\w/g, char => char.toUpperCase());
    
    return title || 'Untitled Document';
  }
} 