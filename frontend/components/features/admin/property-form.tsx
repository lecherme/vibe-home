"use client";

import React, { useState, useEffect } from "react";
import type { AdminPropertyCreate, AdminPropertyUpdate } from "@/types/admin";
import { cn } from "@/lib/utils";

interface PropertyFormProps {
  initialValues?: AdminPropertyUpdate;
  onSubmit: (data: AdminPropertyCreate) => Promise<void>;
  isLoading: boolean;
}

export function PropertyForm({
  initialValues,
  onSubmit,
  isLoading,
}: PropertyFormProps) {
  const [formData, setFormData] = useState<AdminPropertyCreate>({
    title: "",
    description: "",
    price: 0,
    location: "",
    bedrooms: 0,
    bathrooms: 0,
    area: 0,
    image_url: "",
  });

  const [errors, setErrors] = useState<Partial<Record<keyof AdminPropertyCreate, string>>>({});
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (initialValues) {
      setFormData({
        title: initialValues.title ?? "",
        description: initialValues.description ?? "",
        price: initialValues.price ?? 0,
        location: initialValues.location ?? "",
        bedrooms: initialValues.bedrooms ?? 0,
        bathrooms: initialValues.bathrooms ?? 0,
        area: initialValues.area ?? 0,
        image_url: initialValues.image_url ?? "",
      });
    }
  }, [initialValues]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? parseFloat(value) || 0 : value,
    }));
    // Clear error for this field
    if (errors[name as keyof AdminPropertyCreate]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof AdminPropertyCreate, string>> = {};

    if (!formData.title.trim()) newErrors.title = "Title is required";
    if (!formData.description.trim()) newErrors.description = "Description is required";
    if (formData.price <= 0) newErrors.price = "Price must be positive";
    if (!formData.location.trim()) newErrors.location = "Location is required";
    if (formData.bedrooms < 1) newErrors.bedrooms = "At least 1 bedroom is required";
    if (formData.bathrooms < 1) newErrors.bathrooms = "At least 1 bathroom is required";
    if (formData.area <= 0) newErrors.area = "Area must be positive";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const newErrors: Partial<Record<keyof AdminPropertyCreate, string>> = {};

    if (!formData.title.trim()) newErrors.title = "Title is required";
    if (!formData.description.trim()) newErrors.description = "Description is required";
    if (formData.price <= 0) newErrors.price = "Price must be positive";
    if (!formData.location.trim()) newErrors.location = "Location is required";
    if (formData.bedrooms < 1) newErrors.bedrooms = "At least 1 bedroom is required";
    if (formData.bathrooms < 1) newErrors.bathrooms = "At least 1 bathroom is required";
    if (formData.area <= 0) newErrors.area = "Area must be positive";

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      // Scroll to first error
      const firstErrorField = Object.keys(newErrors)[0];
      const element = document.getElementsByName(firstErrorField)[0];
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        (element as HTMLElement).focus();
      }
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const inputClasses = (fieldName: keyof AdminPropertyCreate) =>
    cn(
      "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors",
      errors[fieldName] ? "border-red-500 bg-red-50" : "border-slate-300 bg-white"
    );

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {formError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
          {formError}
        </div>
      )}

      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-1">Title</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={inputClasses("title")}
          placeholder="e.g. Modern Apartment in Downtown"
          disabled={isLoading}
        />
        {errors.title && <p className="mt-1 text-xs text-red-500 font-medium">{errors.title}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-1">Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          className={cn(inputClasses("description"), "h-32 resize-none")}
          placeholder="Detailed description of the property..."
          disabled={isLoading}
        />
        {errors.description && <p className="mt-1 text-xs text-red-500 font-medium">{errors.description}</p>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Price ($)</label>
          <input
            type="number"
            name="price"
            value={formData.price || ""}
            onChange={handleChange}
            className={inputClasses("price")}
            min="0"
            step="0.01"
            placeholder="0.00"
            disabled={isLoading}
          />
          {errors.price && <p className="mt-1 text-xs text-red-500 font-medium">{errors.price}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Location</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            className={inputClasses("location")}
            placeholder="e.g. San Francisco, CA"
            disabled={isLoading}
          />
          {errors.location && <p className="mt-1 text-xs text-red-500 font-medium">{errors.location}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Bedrooms</label>
          <input
            type="number"
            name="bedrooms"
            value={formData.bedrooms || ""}
            onChange={handleChange}
            className={inputClasses("bedrooms")}
            min="1"
            placeholder="1"
            disabled={isLoading}
          />
          {errors.bedrooms && <p className="mt-1 text-xs text-red-500 font-medium">{errors.bedrooms}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Bathrooms</label>
          <input
            type="number"
            name="bathrooms"
            value={formData.bathrooms || ""}
            onChange={handleChange}
            className={inputClasses("bathrooms")}
            min="1"
            placeholder="1"
            disabled={isLoading}
          />
          {errors.bathrooms && <p className="mt-1 text-xs text-red-500 font-medium">{errors.bathrooms}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Area (sqm)</label>
          <input
            type="number"
            name="area"
            value={formData.area || ""}
            onChange={handleChange}
            className={inputClasses("area")}
            min="0"
            placeholder="0"
            disabled={isLoading}
          />
          {errors.area && <p className="mt-1 text-xs text-red-500 font-medium">{errors.area}</p>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-1">Image URL</label>
        <input
          type="text"
          name="image_url"
          value={formData.image_url}
          onChange={handleChange}
          className={inputClasses("image_url")}
          placeholder="https://images.unsplash.com/..."
          disabled={isLoading}
        />
        {errors.image_url && <p className="mt-1 text-xs text-red-500 font-medium">{errors.image_url}</p>}
      </div>

      <div className="flex justify-end pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            "Save Property"
          )}
        </button>
      </div>
    </form>
  );
}
