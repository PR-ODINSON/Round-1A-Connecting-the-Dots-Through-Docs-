import { Injectable, InternalServerErrorException } from '@nestjs/common';
import axios from 'axios';
import { DocumentStructureDto, HeadingDto } from './dto/document-structure.dto';

@Injectable()
export class PdfExtractionService {
  private readonly pythonServiceUrl: string;

  constructor() {
    // Docker service name or localhost for development
    this.pythonServiceUrl = process.env.PYTHON_SERVICE_URL || 'http://python-parser:8000';
  }

  async extractStructure(file: Express.Multer.File): Promise<DocumentStructureDto> {
    try {
      // Create form data to send to Python microservice
      const FormData = require('form-data');
      const formData = new FormData();
      formData.append('file', file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });

      console.log(`🐍 Sending PDF to Python service: ${this.pythonServiceUrl}/extract-headings`);
      
      // Call Python microservice
      const response = await axios.post(
        `${this.pythonServiceUrl}/extract-headings`,
        formData,
        {
          headers: {
            ...formData.getHeaders(),
          },
          timeout: 60000, // 60 seconds timeout for large PDFs
        },
      );

      const pythonResult = response.data;
      
      // Validate and transform the response
      if (!pythonResult || typeof pythonResult !== 'object') {
        throw new Error('Invalid response from Python service');
      }

      // Transform Python response to our DTO format
      const documentStructure: DocumentStructureDto = {
        title: pythonResult.title || 'Untitled Document',
        headings: (pythonResult.headings || []).map((heading: any): HeadingDto => ({
          type: heading.type || 'H1',
          text: heading.text || '',
          page: heading.page || 1,
        })),
        metadata: {
          totalPages: pythonResult.metadata?.total_pages || 0,
          processingTimeMs: pythonResult.metadata?.processing_time_ms || 0,
          fontMetrics: pythonResult.metadata?.font_metrics || {},
        },
      };

      return documentStructure;
    } catch (error) {
      console.error('Error communicating with Python service:', error);
      
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.detail || error.message;
        
        if (status === 400) {
          throw new Error(`Invalid PDF: ${message}`);
        } else if (status >= 500) {
          throw new Error(`Python service error: ${message}`);
        } else if (error.code === 'ECONNREFUSED') {
          throw new Error('Python service is not reachable. Please ensure the service is running.');
        }
      }
      
      throw new InternalServerErrorException(
        `Failed to extract PDF structure: ${error.message}`,
      );
    }
  }
} 