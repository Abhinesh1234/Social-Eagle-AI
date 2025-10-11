
import { config } from 'dotenv';
import * as path from 'path';

const result = config({
  path: path.resolve(process.cwd(), '.env')
});

if (result.error) {
  console.error('Error loading .env file:', result.error);
  process.exit(1);
}

console.log('Environment variables loaded successfully');
