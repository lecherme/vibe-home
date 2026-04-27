import type { Property } from "@/types/property";

interface PropertyDetailProps {
  property: Property;
}

export function PropertyDetail({ property }: PropertyDetailProps) {
  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Image Gallery */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 p-2">
          {property.images.length > 0 ? (
            <>
              <div className="aspect-[16/10] md:col-span-2 overflow-hidden rounded-lg">
                <img
                  src={property.images[0]}
                  alt={property.title}
                  className="w-full h-full object-cover"
                />
              </div>
              {property.images.slice(1, 3).map((img, index) => (
                <div key={index} className="aspect-[16/10] overflow-hidden rounded-lg hidden md:block">
                  <img
                    src={img}
                    alt={`${property.title} ${index + 2}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </>
          ) : (
            <div className="aspect-[16/10] md:col-span-2 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400">
              No images available
            </div>
          )}
        </div>

        <div className="p-6 md:p-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${
                  property.status === 'available' ? 'bg-green-100 text-green-800' :
                  property.status === 'sold' ? 'bg-red-100 text-red-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {property.status}
                </span>
                <h1 className="text-3xl font-bold text-slate-900">{property.title}</h1>
              </div>
              <p className="text-slate-500 flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {property.location}
              </p>
            </div>
            <div className="text-right">
              <p className="text-slate-500 text-sm mb-1 uppercase tracking-wider font-semibold">Price</p>
              <p className="text-3xl font-bold text-blue-600">${property.price.toLocaleString()}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-6 border-y border-slate-100 mb-8">
            <div className="text-center">
              <p className="text-slate-500 text-xs uppercase mb-1">Bedrooms</p>
              <p className="text-xl font-bold text-slate-900">{property.bedrooms}</p>
            </div>
            <div className="text-center">
              <p className="text-slate-500 text-xs uppercase mb-1">Bathrooms</p>
              <p className="text-xl font-bold text-slate-900">{property.bathrooms}</p>
            </div>
            <div className="text-center">
              <p className="text-slate-500 text-xs uppercase mb-1">Area</p>
              <p className="text-xl font-bold text-slate-900">{property.area_sqm} m²</p>
            </div>
            <div className="text-center">
              <p className="text-slate-500 text-xs uppercase mb-1">Listed On</p>
              <p className="text-xl font-bold text-slate-900">
                {new Date(property.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-4">Description</h2>
            <div className="prose prose-slate max-w-none text-slate-600 whitespace-pre-line">
              {property.description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
