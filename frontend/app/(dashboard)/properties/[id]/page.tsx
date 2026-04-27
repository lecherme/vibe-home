import { propertiesApi, PropertyApiError } from "@/lib/api/properties";
import { PropertyDetail } from "@/components/features/properties/PropertyDetail";
import { notFound } from "next/navigation";
import Link from "next/link";

interface PropertyPageProps {
  params: {
    id: string;
  };
}

export default async function PropertyPage({ params }: PropertyPageProps) {
  try {
    const property = await propertiesApi.get(params.id);

    return (
      <div className="min-h-screen bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 pt-8 sm:px-6 lg:px-8">
          <Link
            href="/properties"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            ← Back to properties
          </Link>
        </div>
        <PropertyDetail property={property} />
      </div>
    );
  } catch (error: any) {
    if (error instanceof PropertyApiError && error.status === 404) {
      notFound();
    }

    return (
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <h3 className="text-lg font-semibold text-red-900">Unable to load property</h3>
          <p className="mt-2 text-sm text-red-700">
            {error.message || "An unexpected error occurred. Please try again later."}
          </p>
          <div className="mt-6">
            <Link
              href="/properties"
              className="rounded-md bg-white px-4 py-2 text-sm font-medium text-slate-900 shadow-sm border border-slate-200 hover:bg-slate-50"
            >
              Back to list
            </Link>
          </div>
        </div>
      </div>
    );
  }
}
