import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],

    server: {
      host: "0.0.0.0",
      proxy: {
        "/api/students": {
          target: env.STUDENT_SERVICE_URL || "http://student-service:8000",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/students/, "/students")
        },
        "/api/courses": {
          target: env.COURSE_SERVICE_URL || "http://course-service:8000",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/courses/, "/courses")
        }
      }
    },

    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/setupTests.js"
    }
  };
});