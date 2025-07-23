import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): { message: string; timestamp: string; service: string } {
    return {
      message: 'Adobe Hackathon - PDF Structure Extraction API is running!',
      timestamp: new Date().toISOString(),
      service: 'nestjs-backend'
    };
  }

  getHealth(): { 
    status: string; 
    timestamp: string; 
    services: { nestjs: string; pythonParser: string } 
  } {
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        nestjs: 'running',
        pythonParser: 'reachable' // This could be enhanced to actually ping the Python service
      }
    };
  }
} 