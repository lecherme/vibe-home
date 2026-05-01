"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/api/admin";
import { PropertyForm } from "@/components/features/admin/property-form";
import type { AdminPropertyCreate } from "@/types/admin";

export default function NewPropertyPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: AdminPropertyCreate) => {
    setIsLoading(true);
    try {
      await adminApi.createProperty(data);
      router.push("/admin/properties");
    } catch (err) {
      // Error handling is managed by the PropertyForm component's catch block,
      // but we re-throw to ensure the form knows an error occurred if needed.
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center text-sm font-medium text-slate-500 hover:text-slate-700 transition-colors"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
            Back to list
          </button>
          <h1 className="text-3xl font-bold text-slate-900 mt-4">Add New Property</h1>
          <p className="text-slate-500 mt-2">Fill in the details below to create a new property listing.</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <PropertyForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
