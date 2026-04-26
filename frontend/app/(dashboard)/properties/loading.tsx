import React from "react";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";

export default function Loading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-900">Properties</h1>
      <PropertyListSkeleton />
    </div>
  );
}
