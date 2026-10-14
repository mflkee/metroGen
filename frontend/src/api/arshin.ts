import { apiRequest } from "@/api/client";

export type ArshinStatus = {
  available: boolean;
  message: string | null;
};

export async function fetchArshinStatus(token: string): Promise<ArshinStatus> {
  const response = await apiRequest<{ available: boolean; message: string | null }>("/resolve/status", {
    method: "GET",
    token,
  });
  return {
    available: response.available,
    message: response.message,
  };
}
