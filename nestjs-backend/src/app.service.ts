import { Injectable, Logger } from '@nestjs/common';
import axios from 'axios';

@Injectable()
export class AppService {
  private readonly logger = new Logger(AppService.name);
  private readonly pythonServiceUrl: string;

  constructor() {
    this.pythonServiceUrl = process.env.PYTHON_SERVICE_URL || 'http://python-parser:8000';
  }

  getHello(): { message: string; timestamp: string; service: string } {
    return {
      message: 'Adobe Hackathon - PDF Structure Extraction API is running!',
      timestamp: new Date().toISOString(),
      service: 'nestjs-backend'
    };
  }

  async getHealth(): Promise<{ 
    status: string; 
    timestamp: string; 
    services: { nestjs: string; pythonParser: string };
    pythonServiceUrl: string;
  }> {
    let pythonStatus = 'unreachable';
    
    try {
      // Try to ping the Python service
      const response = await axios.get(`${this.pythonServiceUrl}/health`, {
        timeout: 5000,
      });
      
      if (response.status === 200) {
        pythonStatus = 'healthy';
      } else {
        pythonStatus = 'unhealthy';
      }
    } catch (error) {
      this.logger.warn(`Python service health check failed: ${error.message}`);
      pythonStatus = 'unreachable';
    }

    return {
      status: pythonStatus === 'healthy' ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services: {
        nestjs: 'running',
        pythonParser: pythonStatus
      },
      pythonServiceUrl: this.pythonServiceUrl
    };
  }
} 