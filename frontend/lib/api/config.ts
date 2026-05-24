const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL;

if (!configuredApiUrl) {
  throw new Error("NEXT_PUBLIC_API_URL is not configured");
}

export const apiUrl = configuredApiUrl;
