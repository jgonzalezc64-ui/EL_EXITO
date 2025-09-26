import api from "../../api/http";
import type { Categoria, CategoriaCreate, CategoriaUpdate } from "../../types/catalogos/categorias";

type Paginated<T> = { count: number; next: string | null; previous: string | null; results: T[] };

export async function listCategorias(): Promise<Categoria[]> {
  const { data } = await api.get<Paginated<Categoria> | Categoria[]>("/catalogos/categorias/");
  // DRF con paginación -> trae {results: [...]}
  return (data as Paginated<Categoria>).results ?? (data as Categoria[]);
}

export async function createCategoria(payload: CategoriaCreate): Promise<Categoria> {
  const { data } = await api.post<Categoria>("/catalogos/categorias/", payload);
  return data;
}

export async function updateCategoria(id: number, payload: CategoriaUpdate): Promise<Categoria> {
  const { data } = await api.patch<Categoria>(`/catalogos/categorias/${id}/`, payload);
  return data;
}

export async function toggleCategoria(id: number, activo: boolean): Promise<Categoria> {
  const { data } = await api.patch<Categoria>(`/catalogos/categorias/${id}/`, { activo });
  return data;
}

export async function deleteCategoria(id: number): Promise<void> {
  await api.delete(`/catalogos/categorias/${id}/`);
}