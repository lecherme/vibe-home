"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import { adminApi } from "@/lib/api/admin";
import type { Property } from "@/types/property";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import { PaginationControls } from "@/components/features/common/PaginationControls";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

function parsePageParam(value: string | null) {
  const page = Number(value);
  return Number.isInteger(page) && page > 0 ? page : 1;
}

export default function AdminPropertiesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [properties, setProperties] = useState<Property[]>([]);
  const [page, setPage] = useState(() => parsePageParam(searchParams.get("page")));
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const nextPage = parsePageParam(searchParams.get("page"));
    setPage((currentPage) => (currentPage === nextPage ? currentPage : nextPage));
  }, [searchParams]);

  useEffect(() => {
    fetchProperties(page);
  }, [page]);

  const updatePage = (nextPage: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(nextPage));
    setPage(nextPage);
    router.push(`/admin/properties?${params.toString()}`);
  };

  const fetchProperties = async (pageToFetch: number) => {
    try {
      setIsLoading(true);
      const data = await propertiesApi.list(pageToFetch, PAGE_SIZE);
      setProperties(data.items);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError("Failed to fetch properties. Please try again later.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    const previousProperties = [...properties];
    const isLastOnNonFirstPage = properties.length === 1 && page > 1;

    try {
      await adminApi.deleteProperty(id);
      if (isLastOnNonFirstPage) {
        updatePage(page - 1);
      } else {
        setProperties(properties.filter((p) => p.id !== id));
        await fetchProperties(page);
      }
    } catch (err) {
      setError("Failed to delete property. Please try again.");
      setProperties(previousProperties);
      console.error(err);
    } finally {
      setDeletingId(null);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Manage Properties</h1>
        </div>
        <PropertyListSkeleton />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <h1 className="text-3xl font-bold text-slate-900">Manage Properties</h1>
        <Link
          href="/admin/properties/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-md hover:bg-blue-700 transition-colors shadow-sm"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Property
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-12 flex flex-col items-center text-center mb-8">
          <div className="mb-4 text-red-400">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-red-800 font-bold text-xl mb-2">Management console error</h3>
          <p className="text-red-700 mb-6 max-w-md">{error}</p>
          <button 
            onClick={() => fetchProperties(page)}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        </div>
      )}

      {properties.length === 0 && !isLoading && !error && deletingId === null ? (
        <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="mb-4 text-slate-300">
            <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">No properties yet</h3>
          <p className="text-slate-500 max-w-md mx-auto mb-8">Get started by creating your first property listing for the marketplace.</p>
          <Link
            href="/admin/properties/new"
            className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
            Create New Property
          </Link>
        </div>
      ) : properties.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1024px] table-fixed divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="w-64 px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Property</th>
                  <th scope="col" className="w-52 px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Location</th>
                  <th scope="col" className="w-36 px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Price</th>
                  <th scope="col" className="w-28 px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="w-40 px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {properties.map((property) => (
                  <tr key={property.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 max-w-0">
                      <div className="flex items-center min-w-0">
                        <div className="h-10 w-10 flex-shrink-0">
                          {property.images && property.images.length > 0 ? (
                            <img className="h-10 w-10 rounded-md object-cover" src={property.images[0]} alt="" />
                          ) : (
                            <div className="h-10 w-10 rounded-md bg-slate-200 flex items-center justify-center">
                              <svg className="h-6 w-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                          )}
                        </div>
                        <div className="ml-4 min-w-0">
                          <div className="text-sm font-semibold text-slate-900 truncate">{property.title}</div>
                          <div className="text-xs text-slate-500 truncate">{property.description}</div>
                        </div>
                      </div>
                    </td>
                    <td className="w-52 px-6 py-4 max-w-0">
                      <div className="text-sm text-slate-600 truncate">{property.location}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-semibold text-slate-900">${property.price.toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={cn(
                        "px-2.5 py-0.5 inline-flex text-xs font-semibold rounded-full",
                        property.status === 'available' ? 'bg-green-100 text-green-800' : 
                        property.status === 'sold' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                      )}>
                        {property.status}
                      </span>
                    </td>
                    <td className="w-40 px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {deletingId === property.id ? (
                        <div className="inline-flex items-center gap-2">
                          <span className="text-slate-500 text-xs">Sure?</span>
                          <button
                            onClick={() => handleDelete(property.id)}
                            className="text-red-600 hover:text-red-900 font-bold"
                          >
                            Yes
                          </button>
                          <button
                            onClick={() => setDeletingId(null)}
                            className="text-slate-600 hover:text-slate-900"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-4">
                          <Link
                            href={`/admin/properties/${property.id}/edit`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </Link>
                          <button
                            onClick={() => setDeletingId(property.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <PaginationControls
            page={page}
            totalPages={totalPages}
            onPageChange={updatePage}
            isLoading={isLoading}
            className="px-6 py-4 border-t border-slate-200"
          />
        </div>
      ) : null}
    </div>
  );
}
