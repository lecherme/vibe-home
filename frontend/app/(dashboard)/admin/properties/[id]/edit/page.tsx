"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import { adminApi } from "@/lib/api/admin";
import { PropertyForm } from "@/components/features/admin/property-form";
import type { AdminPropertyCreate, AdminPropertyUpdate } from "@/types/admin";

export default function EditPropertyPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  const [initialValues, setInitialValues] = useState<AdminPropertyUpdate | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchProperty();
    }
  }, [id]);

  const fetchProperty = async () => {
    try {
      setIsLoading(true);
      const property = await propertiesApi.get(id);
      
      // Map Property to AdminPropertyUpdate
      // Note: Backend uses area_sqm and images[] but Admin API expects area and image_url
      setInitialValues({
        title: property.title,
        description: property.description,
        price: property.price,
        location: property.location,
        bedrooms: property.bedrooms,
        bathrooms: property.bathrooms,
        area: property.area_sqm,
        image_url: property.images && property.images.length > 0 ? property.images[0] : "",
      });
      setError(null);
    } catch (err) {
      setError("Failed to fetch property details. The property may not exist.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data: AdminPropertyCreate) => {
    setIsSaving(true);
    try {
      await adminApi.updateProperty(id, data);
      router.push("/admin/properties");
    } catch (err) {
      // Error handling is managed by the PropertyForm component's catch block
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto flex items-center justify-center min-h-[400px]">
          <div className="flex flex-col items-center">
            <svg className="animate-spin h-10 w-10 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-slate-500 font-medium">Loading property details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !initialValues) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto text-center py-16 bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="p-4 bg-red-50 text-red-700 rounded-md inline-block mb-6">
            <p className="font-medium">{error || "Property not found"}</p>
          </div>
          <div className="mt-4">
            <button
              onClick={() => router.push("/admin/properties")}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-md hover:bg-slate-200 font-medium transition-colors"
            >
              Back to Properties
            </button>
          </div>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-slate-900 mt-4">Edit Property</h1>
          <p className="text-slate-500 mt-2">Modify the property details and save your changes.</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <PropertyForm 
            initialValues={initialValues} 
            onSubmit={handleSubmit} 
            isLoading={isSaving} 
          />
        </div>
      </div>
    </div>
  );
}
