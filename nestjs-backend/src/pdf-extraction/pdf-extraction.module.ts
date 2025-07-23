import { Module } from '@nestjs/common';
import { PdfExtractionController } from './pdf-extraction.controller';
import { PdfExtractionService } from './pdf-extraction.service';

@Module({
  controllers: [PdfExtractionController],
  providers: [PdfExtractionService],
})
export class PdfExtractionModule {} 