import { propertiesApi } from "@/lib/api/properties";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import Link from "next/link";
import { Suspense } from "react";

interface PropertiesPageProps {
  searchParams: {
    page?: string;
  };
}

const PAGE_SIZE = 12;

async function PropertyList({ page }: { page: number }) {
  try {
    const data = await propertiesApi.list(page, PAGE_SIZE);

    if (data.items.length === 0) {
      return (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-200 p-12 text-center">
          <h3 className="text-lg font-semibold text-slate-900">No properties found</h3>
          <p className="mt-2 text-sm text-slate-500">
            We couldn't find any properties at the moment. Please check back later.
          </p>
        </div>
      );
    }

    const totalPages = Math.ceil(data.total / PAGE_SIZE);

    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data.items.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4">
            <Link
              href={`/properties?page=${page - 1}`}
              className={`rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 ${
                page <= 1 ? "pointer-events-none opacity-50" : ""
              }`}
            >
              Previous
            </Link>
            <span className="text-sm text-slate-600">
              Page {page} of {totalPages}
            </span>
            <Link
              href={`/properties?page=${page + 1}`}
              className={`rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 ${
                page >= totalPages ? "pointer-events-none opacity-50" : ""
              }`}
            >
              Next
            </Link>
          </div>
        )}
      </div>
    );
  } catch (error: any) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <h3 className="text-lg font-semibold text-red-900">Unable to load properties</h3>
        <p className="mt-2 text-sm text-red-700">
          {error.message || "An unexpected error occurred. Please try again later."}
        </p>
      </div>
    );
  }
}

export default function PropertiesPage({ searchParams }: PropertiesPageProps) {
  const page = Number(searchParams.page) || 1;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Properties</h1>
        <p className="mt-2 text-slate-600">
          Browse our collection of available properties.
        </p>
      </div>

      <Suspense fallback={<PropertyListSkeleton />}>
        <PropertyList page={page} />
      </Suspense>
    </div>
  );
}
