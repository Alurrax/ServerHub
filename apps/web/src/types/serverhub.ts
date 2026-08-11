export type SystemStatus = {
  host: {
    hostname: string;
    cpu: {
      percent: number;
      logical_cores: number;
      physical_cores: number;
    };
    memory: {
      total_gb: number;
      used_gb: number;
      available_gb: number;
      percent: number;
    };
    swap: {
      total_gb: number;
      used_gb: number;
      free_gb: number;
      percent: number;
    };
    disk: {
      mount: string;
      total_gb: number;
      used_gb: number;
      free_gb: number;
      percent: number;
    };
    uptime_seconds: number;
  };
};

export type DockerContainer = {
  id: string;
  name: string;
  image: string;
  status: string;
  state: string;
  ports?: string;
  created_at?: string;
};

export type DockerContainersResponse = {
  containers: DockerContainer[];
  count: number;
};

export type DockerStats = {
  name: string;
  cpu_percent: number;
  memory: {
    usage: string;
    limit: string;
    percent: number;
  };
  network_io: string;
  block_io: string;
  pids: number;
};

export type ContainerWithStats = DockerContainer & {
  stats?: DockerStats;
};

export type SystemService = {
  unit: string;
  name: string;
  load: string;
  active: string;
  sub: string;
  description: string;
};

export type ServicesResponse = {
  services: SystemService[];
  count: number;
};
