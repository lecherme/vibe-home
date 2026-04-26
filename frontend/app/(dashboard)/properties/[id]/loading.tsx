import React from "react";

export default function Loading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 animate-pulse">
      <div className="lg:grid lg:grid-cols-2 lg:items-start lg:gap-x-8">
        <div className="aspect-h-3 aspect-w-4 overflow-hidden rounded-lg bg-gray-200" />
        <div className="mt-10 px-4 sm:mt-16 sm:px-0 lg:mt-0 space-y-6">
          <div className="h-10 w-3/4 bg-gray-200 rounded" />
          <div className="h-6 w-1/2 bg-gray-200 rounded" />
          <div className="h-12 w-1/4 bg-gray-200 rounded" />
          <div className="grid grid-cols-4 gap-4 py-6 border-y border-gray-200">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded" />
            ))}
          </div>
          <div className="space-y-4">
            <div className="h-4 w-full bg-gray-200 rounded" />
            <div className="h-4 w-full bg-gray-200 rounded" />
            <div className="h-4 w-2/3 bg-gray-200 rounded" />
          </div>
        </div>
      </div>
    </div>
  );
}
