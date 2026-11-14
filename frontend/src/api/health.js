
import client from "./client";

export async function getHealth() {
  const response = await client.get("/health");
  return response.data;
}
