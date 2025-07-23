import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Enable CORS for frontend integration
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:3001'], // Frontend ports
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type'],
  });

  // Global validation pipe
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));

  // API documentation with Swagger
  const config = new DocumentBuilder()
    .setTitle('Adobe Hackathon - PDF Structure Extraction API')
    .setDescription('API for extracting document structure from PDF files')
    .setVersion('1.0')
    .addTag('pdf-extraction')
    .build();
  
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  const port = process.env.PORT || 3000;
  await app.listen(port);
  console.log(`🚀 NestJS Backend running on port ${port}`);
  console.log(`📖 API Documentation available at http://localhost:${port}/api`);
}

bootstrap(); 