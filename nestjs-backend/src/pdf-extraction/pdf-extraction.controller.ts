import {
  Controller,
  Post,
  UseInterceptors,
  UploadedFile,
  BadRequestException,
  InternalServerErrorException,
  HttpStatus,
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
  constructor(private readonly pdfExtractionService: PdfExtractionService) {}

  @Post('parse-pdf')
  @UseInterceptors(FileInterceptor('file'))
  @ApiOperation({ summary: 'Extract document structure from PDF' })
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
          description: 'PDF file (max 50 pages)',
        },
      },
    },
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: 'Document structure extracted successfully',
    type: DocumentStructureDto,
  })
  @ApiResponse({
    status: HttpStatus.BAD_REQUEST,
    description: 'Invalid file or file format',
  })
  @ApiResponse({
    status: HttpStatus.INTERNAL_SERVER_ERROR,
    description: 'Error processing PDF',
  })
  async parsePdf(
    @UploadedFile() file: Express.Multer.File,
  ): Promise<DocumentStructureDto> {
    if (!file) {
      throw new BadRequestException('No file provided');
    }

    if (file.mimetype !== 'application/pdf') {
      throw new BadRequestException('File must be a PDF');
    }

    // Basic file size validation (50MB max for 50 pages)
    const maxSizeInBytes = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSizeInBytes) {
      throw new BadRequestException(
        'File too large. Maximum size is 50MB (~50 pages)',
      );
    }

    try {
      console.log(`📄 Processing PDF: ${file.originalname} (${file.size} bytes)`);
      const result = await this.pdfExtractionService.extractStructure(file);
      console.log(`✅ Successfully processed PDF with ${result.headings.length} headings`);
      return result;
    } catch (error) {
      console.error('❌ Error processing PDF:', error);
      throw new InternalServerErrorException(
        'Failed to process PDF. Please ensure the file is valid and not corrupted.',
      );
    }
  }
} 