"use client";

import React, { useState, useEffect, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { AdminPropertyCreate, AdminPropertyUpdate } from "@/types/admin";
import { uploadPropertyImage } from "@/lib/api/admin";
import { propertySchema, type PropertyFormValues } from "@/lib/schemas/property";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2, Plus, Trash2, Upload } from "lucide-react";

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
  const [formError, setFormError] = useState<string | null>(null);
  const [uploadingIndex, setUploadingIndex] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pendingUploadIndexRef = useRef<number>(-1);

  const form = useForm<PropertyFormValues>({
    resolver: zodResolver(propertySchema),
    defaultValues: {
      title: "",
      description: "",
      price: 0,
      location: "",
      bedrooms: 0,
      bathrooms: 0,
      area: 0,
      images: [""],
    },
  });

  useEffect(() => {
    if (initialValues) {
      form.reset({
        title: initialValues.title ?? "",
        description: initialValues.description ?? "",
        price: initialValues.price ?? 0,
        location: initialValues.location ?? "",
        bedrooms: initialValues.bedrooms ?? 0,
        bathrooms: initialValues.bathrooms ?? 0,
        area: initialValues.area ?? 0,
        images: initialValues.images && initialValues.images.length > 0 ? initialValues.images : [""],
      });
    }
  }, [initialValues, form]);

  const onFormSubmit = async (values: PropertyFormValues) => {
    setFormError(null);
    try {
      await onSubmit({
        ...values,
        images: values.images.map((img) => img.trim()).filter(Boolean),
      });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const triggerUpload = (index: number) => {
    pendingUploadIndexRef.current = index;
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    const index = pendingUploadIndexRef.current;
    e.target.value = "";
    if (!file || index < 0) return;

    setUploadingIndex(index);
    try {
      const { url } = await uploadPropertyImage(file);
      const currentImages = form.getValues("images");
      const newImages = [...currentImages];
      newImages[index] = url;
      form.setValue("images", newImages, { shouldValidate: true });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploadingIndex(null);
    }
  };

  const handleAddImage = () => {
    const currentImages = form.getValues("images");
    if (currentImages.length < 5) {
      form.setValue("images", [...currentImages, ""], { shouldValidate: true });
    }
  };

  const handleRemoveImage = (index: number) => {
    const currentImages = form.getValues("images");
    const newImages = currentImages.length > 1
      ? currentImages.filter((_, i) => i !== index)
      : [""];
    form.setValue("images", newImages, { shouldValidate: true });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onFormSubmit)} className="space-y-6">
        {formError && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {formError}
          </div>
        )}

        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="e.g. Modern Apartment in Downtown" {...field} disabled={isLoading} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Detailed description of the property..."
                  className="h-32 resize-none"
                  {...field}
                  disabled={isLoading}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="price"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price ($)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    {...field}
                    value={field.value || ""}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="location"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Location</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. San Francisco, CA" {...field} disabled={isLoading} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="bedrooms"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Bedrooms</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="1"
                    {...field}
                    value={field.value || ""}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10) || 0)}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="bathrooms"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Bathrooms</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="1"
                    {...field}
                    value={field.value || ""}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10) || 0)}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="area"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Area (sqm)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="0"
                    {...field}
                    value={field.value || ""}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div>
          <div className="flex items-center justify-between gap-3 mb-1">
            <label className="text-sm font-medium leading-none">Image URLs</label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddImage}
              disabled={isLoading || form.watch("images").length >= 5}
            >
              <Plus className="h-4 w-4 mr-1" /> Add
            </Button>
          </div>
          <div className="space-y-2">
            {form.watch("images").map((_, index) => (
              <div key={index} className="flex gap-2">
                <FormField
                  control={form.control}
                  name={`images.${index}`}
                  render={({ field }) => (
                    <FormItem className="flex-1">
                      <FormControl>
                        <Input
                          placeholder="https://images.unsplash.com/..."
                          {...field}
                          disabled={isLoading}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => triggerUpload(index)}
                  disabled={isLoading || uploadingIndex !== null}
                >
                  {uploadingIndex === index ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  <span className="ml-2 hidden sm:inline">
                    {uploadingIndex === index ? "Uploading..." : "Upload"}
                  </span>
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => handleRemoveImage(index)}
                  disabled={isLoading || form.watch("images").length <= 1}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
          <FormField
            control={form.control}
            name="images"
            render={() => (
              <FormItem>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="flex justify-end pt-4">
          <Button
            type="submit"
            disabled={form.formState.isSubmitting || uploadingIndex !== null}
            className="px-8"
          >
            {form.formState.isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              "Save Property"
            )}
          </Button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handleFileChange}
        />
      </form>
    </Form>
  );
}
