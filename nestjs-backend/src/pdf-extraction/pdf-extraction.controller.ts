import {
  Controller,
  Post,
  UseInterceptors,
  UploadedFile,
  BadRequestException,
  InternalServerErrorException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiConsumes,
  ApiBody,
} from '@nestjs/swagger';
import { PdfExtractionService } from './pdf-extraction.service';
import { DocumentStructureDto } from './dto/document-structure.dto';

@ApiTags('pdf-extraction')
@Controller('pdf-extraction')
export class PdfExtractionController {
  private readonly logger = new Logger(PdfExtractionController.name);

  constructor(private readonly pdfExtractionService: PdfExtractionService) {}

  @Post('parse-pdf')
  @UseInterceptors(FileInterceptor('file', {
    limits: {
      fileSize: 50 * 1024 * 1024, // 50MB limit
    },
    fileFilter: (req, file, callback) => {
      if (file.mimetype !== 'application/pdf') {
        return callback(new BadRequestException('Only PDF files are allowed'), false);
      }
      callback(null, true);
    },
  }))
  @ApiOperation({ 
    summary: 'Extract document structure from PDF',
    description: `
    **Adobe Hackathon - Round 1A: Document Structure Extraction**
    
    This endpoint processes PDF files and extracts structured document information including:
    - Document title (extracted from content or filename)
    - Hierarchical headings (H1, H2, H3) with page numbers
    - Font metrics and processing statistics
    
    **Processing Features:**
    - Advanced NLP-based heading classification
    - Font size and style analysis
    - Pattern recognition for numbered sections
    - Intelligent title extraction
    - Comprehensive error handling
    
    **Limitations:**
    - Maximum file size: 50MB
    - Maximum pages: 50 pages
    - Supported format: PDF only
    - Processing timeout: 2 minutes
    `
  })
  @ApiConsumes('multipart/form-data')
  @ApiBody({
    description: 'PDF file to extract structure from',
    type: 'multipart/form-data',
    schema: {
      type: 'object',
      properties: {
        file: {
          type: 'string',
          format: 'binary',
          description: 'PDF file (≤ 50MB, ≤ 50 pages)',
        },
      },
      required: ['file'],
    },
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Document structure extracted successfully',
    type: DocumentStructureDto,
          schema: {
        example: {
          title: "AI in Healthcare: A Comprehensive Review",
          outline: [
            {
              level: "H1",
              text: "Introduction",
              page: 1
            },
            {
              level: "H2",
              text: "Problem Statement",
              page: 2
            },
            {
              level: "H3",
              text: "Scope and Limitations",
              page: 3
            }
          ],
        metadata: {
          totalPages: 25,
          processingTimeMs: 1250.5,
          fontMetrics: {
            "Times-Bold": {
              avg_size: 18.2,
              max_size: 24.0,
              min_size: 16.0,
              count: 7
            },
            "Arial": {
              avg_size: 12.0,
              max_size: 12.0,
              min_size: 12.0,
              count: 156
            }
          }
        }
      }
    }
  })
  @ApiResponse({
    status: HttpStatus.BAD_REQUEST,
    description: 'Invalid file, format, or size',
    schema: {
      example: {
        statusCode: 400,
        message: "File too large: 55.2MB. Maximum allowed: 50MB",
        error: "Bad Request"
      }
    }
  })
  @ApiResponse({
    status: HttpStatus.INTERNAL_SERVER_ERROR,
    description: 'Error processing PDF or Python service unavailable',
    schema: {
      example: {
        statusCode: 500,
        message: "Python service is not reachable. Please ensure the service is running.",
        error: "Internal Server Error"
      }
    }
  })
  async parsePdf(
    @UploadedFile() file: Express.Multer.File,
  ): Promise<DocumentStructureDto> {
    const startTime = Date.now();
    
    // Enhanced file validation
    if (!file) {
      throw new BadRequestException('No file provided');
    }

    if (file.mimetype !== 'application/pdf') {
      throw new BadRequestException('File must be a PDF');
    }

    // Check for empty file
    if (!file.buffer || file.buffer.length === 0) {
      throw new BadRequestException('Empty file provided');
    }

    // Enhanced file size validation
    const maxSizeInBytes = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSizeInBytes) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
      throw new BadRequestException(
        `File too large: ${fileSizeMB}MB. Maximum allowed: 50MB`
      );
    }

    // Log processing start
    this.logger.log(`📄 Starting PDF processing: ${file.originalname} (${file.size} bytes)`);

    try {
      const result = await this.pdfExtractionService.extractStructure(file);
      
      const processingTime = Date.now() - startTime;
             this.logger.log(
         `✅ Successfully processed PDF: ${result.title} | ` +
         `${result.outline.length} headings | ${processingTime}ms`
       );
      
      return result;
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.logger.error(
        `❌ Failed to process PDF ${file.originalname} after ${processingTime}ms:`,
        error.stack
      );

      // Re-throw known exceptions
      if (error instanceof BadRequestException || error instanceof InternalServerErrorException) {
        throw error;
      }

      // Handle unexpected errors
      throw new InternalServerErrorException(
        'An unexpected error occurred while processing the PDF. Please try again or contact support if the issue persists.'
      );
    }
  }
} 