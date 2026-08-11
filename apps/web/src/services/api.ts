import type {
  ContainerWithStats,
  DisksResponse,
  DockerContainersResponse,
  DockerStats,
  ServicesResponse,
  SystemStatus,
} from "../types/serverhub";

export const API_URL = "http://192.168.1.9:8000";

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_URL}${path}`,
    options,
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ?? "Error comunicándose con ServerHub",
    );
  }

  return data as T;
}

export function getSystemStatus() {
  return request<SystemStatus>("/system/status");
}

export async function getContainersWithStats() {
  const data = await request<DockerContainersResponse>(
    "/system/docker/containers",
  );

  const containers: ContainerWithStats[] =
    await Promise.all(
      data.containers.map(async (container) => {
        if (container.state !== "running") {
          return container;
        }

        try {
          const stats = await request<DockerStats>(
            `/system/docker/containers/${container.name}/stats`,
          );

          return {
            ...container,
            stats,
          };
        } catch {
          return container;
        }
      }),
    );

  return {
    containers,
    count: data.count,
  };
}

export function restartContainer(name: string) {
  return request<{
    container: string;
    action: string;
    status: string;
  }>(
    `/system/docker/containers/${name}/restart`,
    {
      method: "POST",
    },
  );
}

export function getServices() {
  return request<ServicesResponse>(
    "/system/services",
  );
}

export function restartService(name: string) {
  return request<{
    service: string;
    action: string;
    status: string;
  }>(
    `/system/services/${name}/restart`,
    {
      method: "POST",
    },
  );
}

export function getDisks() {
  return request<DisksResponse>("/system/disks");
}
