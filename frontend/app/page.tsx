"use client";

import { useEffect, useState } from "react";
import { getHealthStatus } from "@/lib/api/health";
import type { HealthResponse } from "@/types/health";

export default function HealthPage() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getHealthStatus()
      .then(setData)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to fetch health status")
      )
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 font-sans">
      <div className="max-w-md w-full p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
        <h1 className="text-2xl font-bold mb-4 text-gray-900">System Health Status</h1>

        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700">Backend Status:</span>
            {isLoading ? (
              <span className="text-blue-500 animate-pulse">Checking...</span>
            ) : data?.status === "ok" ? (
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-semibold uppercase">
                {data.status}
              </span>
            ) : (
              <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm font-semibold uppercase">
                Error
              </span>
            )}
          </div>

          {!isLoading && error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
