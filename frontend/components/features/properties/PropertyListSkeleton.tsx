import React from "react";

export function PropertyListSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm animate-pulse"
        >
          <div className="aspect-video w-full bg-gray-200" />
          <div className="flex flex-1 flex-col p-4 space-y-3">
            <div className="h-6 w-3/4 bg-gray-200 rounded" />
            <div className="h-4 w-1/2 bg-gray-200 rounded" />
            <div className="pt-4 flex justify-between items-center">
              <div className="h-6 w-1/4 bg-gray-200 rounded" />
              <div className="flex gap-2">
                <div className="h-4 w-8 bg-gray-200 rounded" />
                <div className="h-4 w-8 bg-gray-200 rounded" />
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
