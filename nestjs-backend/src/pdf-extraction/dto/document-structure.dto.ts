import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsNumber, IsArray, ValidateNested, IsOptional, IsObject } from 'class-validator';
import { Type } from 'class-transformer';

export class HeadingDto {
  @ApiProperty({
    description: 'Heading level (H1, H2, H3)',
    enum: ['H1', 'H2', 'H3'],
    example: 'H1',
  })
  @IsString()
  level: 'H1' | 'H2' | 'H3';

  @ApiProperty({
    description: 'Heading text content',
    example: 'Introduction',
  })
  @IsString()
  text: string;

  @ApiProperty({
    description: 'Page number where the heading appears',
    example: 1,
  })
  @IsNumber()
  page: number;
}

export class MetadataDto {
  @ApiProperty({
    description: 'Total number of pages in the document',
    example: 25,
  })
  @IsNumber()
  totalPages: number;

  @ApiProperty({
    description: 'Processing time in milliseconds',
    example: 1250,
  })
  @IsNumber()
  processingTimeMs: number;

  @ApiProperty({
    description: 'Font metrics used for heading classification',
    example: { 'Arial-Bold': { count: 15, avgSize: 18 } },
  })
  @IsOptional()
  @IsObject()
  fontMetrics?: Record<string, any>;
}

export class DocumentStructureDto {
  @ApiProperty({
    description: 'Document title extracted from the PDF',
    example: 'Adobe Product Documentation',
  })
  @IsString()
  title: string;

  @ApiProperty({
    description: 'Document outline with detected headings in hierarchical order',
    type: [HeadingDto],
  })
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => HeadingDto)
  outline: HeadingDto[];

  @ApiProperty({
    description: 'Additional metadata about the document processing',
    type: MetadataDto,
  })
  @IsOptional()
  @ValidateNested()
  @Type(() => MetadataDto)
  metadata?: MetadataDto;
} 