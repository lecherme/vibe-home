import Link from "next/link";
import type { Property } from "@/types/property";
import { FavoriteButton } from "@/components/features/favorites/favorite-button";

interface PropertyCardProps {
  property: Property;
  isFavorited?: boolean;
  onFavoriteToggle?: (isFavorited: boolean) => void;
}

export function PropertyCard({ property, isFavorited, onFavoriteToggle }: PropertyCardProps) {
  const firstImage = property.images[0] || "/images/properties/property-placeholder-exterior.svg";

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = "/images/properties/property-placeholder-exterior.svg";
  };

  return (
    <div className="group relative bg-white rounded-lg border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
      <Link 
        href={`/properties/${property.id}`}
        className="block"
      >
        <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
          <img
            src={firstImage}
            alt={property.title}
            onError={handleImageError}
            className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300"
          />
        </div>
      </Link>
      
      <div className="absolute top-3 right-3 z-10">
        <FavoriteButton propertyId={property.id} initialIsFavorited={isFavorited} onToggle={onFavoriteToggle} />
      </div>

      <Link 
        href={`/properties/${property.id}`}
        className="block p-4"
      >
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-lg text-slate-900 truncate flex-1 mr-2">
            {property.title}
          </h3>
          <span className="text-blue-600 font-bold">
            ${property.price.toLocaleString()}
          </span>
        </div>
        <p className="text-slate-500 text-sm mb-4 truncate">
          {property.location}
        </p>
        <div className="flex items-center gap-4 text-slate-600 text-sm">
          <div className="flex items-center gap-1">
            <span className="font-medium">{property.bedrooms}</span>
            <span>bed</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="font-medium">{property.bathrooms}</span>
            <span>bath</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="font-medium">{property.area_sqm}</span>
            <span>m²</span>
          </div>
        </div>
      </Link>
    </div>
  );
}
