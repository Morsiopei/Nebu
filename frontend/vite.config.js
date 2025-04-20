import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode (development, production)
  // Make sure VITE_ variables are used in .env for client-side exposure
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      port: 3000, // Development server port
      open: true, // Automatically open browser
      proxy: {
        // Proxy API requests starting with '/api' during development
        // to the backend API Gateway running on port 8000
        '/api': {
          target: env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000', // Target the gateway base URL
          changeOrigin: true, // Needed for virtual hosted sites
          // rewrite: (path) => path.replace(/^\/api/, ''), // Optional: if gateway doesn't expect /api prefix
        },
      },
    },
    // Optional: Define path aliases
    resolve: {
      alias: {
        '@': '/src', // Example: import Button from '@/components/common/Button'
      },
    },
     define: {
       // Make environment variables available in client-side code
       // Filter only VITE_ prefixed variables for security
       'process.env': Object.keys(env)
         .filter(key => key.startsWith('VITE_'))
         .reduce((acc, key) => {
           acc[`process.env.${key}`] = JSON.stringify(env[key]);
           return acc;
         }, {}),
     }
  };
});
