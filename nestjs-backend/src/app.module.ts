import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { PdfExtractionModule } from './pdf-extraction/pdf-extraction.module';

@Module({
  imports: [PdfExtractionModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {} 