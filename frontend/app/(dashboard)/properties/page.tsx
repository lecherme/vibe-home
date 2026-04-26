import React from "react";
import { propertiesApi } from "@/lib/api/properties";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import Link from "next/link";

interface PropertiesPageProps {
  searchParams: {
    page?: string;
  };
}

export default async function PropertiesPage({
  searchParams,
}: PropertiesPageProps) {
  const page = Number(searchParams.page) || 1;
  const pageSize = 12;

  try {
    const data = await propertiesApi.list(page, pageSize);

    if (data.items.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-20">
          <h2 className="text-2xl font-semibold text-gray-900">No properties found</h2>
          <p className="mt-2 text-gray-500">Check back later for new listings.</p>
        </div>
      );
    }

    const totalPages = Math.ceil(data.total / data.page_size);

    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <h1 className="mb-8 text-3xl font-bold text-gray-900">Properties</h1>
        
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data.items.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>

        {/* Pagination Controls */}
        <div className="mt-12 flex items-center justify-between border-t border-gray-200 pt-8">
          <div className="flex flex-1 justify-between sm:hidden">
            <PaginationLink
              href={`/properties?page=${page - 1}`}
              disabled={page <= 1}
            >
              Previous
            </PaginationLink>
            <PaginationLink
              href={`/properties?page=${page + 1}`}
              disabled={page >= totalPages}
            >
              Next
            </PaginationLink>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(page - 1) * data.page_size + 1}</span> to{" "}
                <span className="font-medium">
                  {Math.min(page * data.page_size, data.total)}
                </span>{" "}
                of <span className="font-medium">{data.total}</span> results
              </p>
            </div>
            <div>
              <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <PaginationLink
                  href={`/properties?page=${page - 1}`}
                  disabled={page <= 1}
                  className="rounded-l-md"
                >
                  <span className="sr-only">Previous</span>
                  <span>&larr;</span>
                </PaginationLink>
                <span className="inline-flex items-center border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700">
                  Page {page} of {totalPages}
                </span>
                <PaginationLink
                  href={`/properties?page=${page + 1}`}
                  disabled={page >= totalPages}
                  className="rounded-r-md"
                >
                  <span className="sr-only">Next</span>
                  <span>&rarr;</span>
                </PaginationLink>
              </nav>
            </div>
          </div>
        </div>
      </div>
    );
  } catch (error) {
    console.error("Failed to fetch properties:", error);
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 text-center">
        <h2 className="text-2xl font-bold text-red-600">Error loading properties</h2>
        <p className="mt-2 text-gray-600">
          We encountered a problem while fetching the property list. Please try again later.
        </p>
        <Link 
          href="/properties" 
          className="mt-6 inline-block rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Retry
        </Link>
      </div>
    );
  }
}

function PaginationLink({ 
  href, 
  disabled, 
  children, 
  className = "" 
}: { 
  href: string; 
  disabled: boolean; 
  children: React.ReactNode;
  className?: string;
}) {
  if (disabled) {
    return (
      <span className={`inline-flex items-center border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-400 cursor-not-allowed ${className}`}>
        {children}
      </span>
    );
  }

  return (
    <Link
      href={href}
      className={`inline-flex items-center border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 ${className}`}
    >
      {children}
    </Link>
  );
}
