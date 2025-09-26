import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../app/useAuth";
import { listCategorias, createCategoria, updateCategoria, toggleCategoria,deleteCategoria } from "../../services/catalogos/categorias";
import type { Categoria } from "../../types/catalogos/categorias";
import "../../theme/catalogos/catalogos.css";

export default function CategoriasPage(){
  const { hasRole } = useAuth();
  const isAdmin = hasRole("ADMIN");
  const [items, setItems] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ nombre:"", descripcion:"" });
  const [filter, setFilter] = useState("");

  const filtered = useMemo(()=>{
    const q = filter.trim().toLowerCase();
    if(!q) return items;
    return items.filter(x =>
      x.nombre.toLowerCase().includes(q) ||
      (x.descripcion || "").toLowerCase().includes(q)
    );
  }, [items, filter]);

  async function load(){
    setLoading(true);
    try{ setItems(await listCategorias()); }
    finally{ setLoading(false); }
  }

  useEffect(()=>{ load(); },[]);

  async function onCreate(e: React.FormEvent){
    e.preventDefault();
    const nombre = form.nombre.trim();
    const descripcion = (form.descripcion || "").trim();
    if(!form.nombre.trim()) return;
    if (!confirm(`¿Guardar nueva categoría?\n\nNombre: "${nombre}"\nDescripción: "${descripcion || "(vacío)"}"`)) {
    return;
  }
    setCreating(true);
    try{
      const created = await createCategoria({ nombre: form.nombre.trim(), descripcion: form.descripcion || undefined, activo: true });
      setItems(prev => [created, ...prev]);
      setForm({ nombre:"", descripcion:"" });
    } finally{
      setCreating(false);
    }
  }

  async function onToggle(id: number, activo: boolean){
    const accion = activo ? "desactivar" : "activar";
    if (!confirm(`¿Seguro que deseas ${accion} esta categoría?`)) return;

    // Optimista + rollback si falla
    const prev = items;
    const provisional = items.map((x) =>
      x.id_categoria === id ? { ...x, activo: !activo } : x
    );
    setItems(provisional);
    try {
      const updated = await toggleCategoria(id, !activo);
      setItems((cur) => cur.map((x) => (x.id_categoria === id ? updated : x)));
    } catch  {
      setItems(prev); // rollback
      alert("No se pudo cambiar el estado. Intenta nuevamente.");
    }
  }

  async function onInlineEdit(id: number, patch: Partial<Categoria>){
    const current = items.find((x) => x.id_categoria === id);
    const isNombre = Object.prototype.hasOwnProperty.call(patch, "nombre");
    const campo = isNombre ? "nombre" : "descripción";

    const nuevo = (isNombre ? (patch as Partial<Categoria>).nombre : (patch as Partial<Categoria>).descripcion) ?? "";
    const anterior = (isNombre ? current?.nombre : current?.descripcion) ?? "";

    if (nuevo === anterior) return; // nada que guardar

    // Confirmar "Guardar" edición
    if (!confirm(`¿Guardar cambios de ${campo}?\n\nAntes: "${anterior}"\nAhora:  "${nuevo}"`)) {
      return;
    }

    // Optimista + rollback si falla
    const prev = items;
    // actualiza localmente con patch
    setItems((cur) =>
      cur.map((x) =>
        x.id_categoria === id ? { ...x, ...(isNombre ? { nombre: nuevo } : { descripcion: nuevo || null }) } : x
      )
    );
    try {
      const updated = await updateCategoria(id, patch);
      setItems((cur) => cur.map((x) => (x.id_categoria === id ? updated : x)));
    } catch  {
      setItems(prev); // rollback
      alert("No se pudo guardar el cambio. Intenta nuevamente.");
    }
  }

  return (
    <div style={{ display:"grid", gap: 16 }}>
      <div className="cat-toolbar">
        <div>
          <h2 className="h1" style={{ margin:0 }}>Categorías</h2>
          <div className="subtle">Gestión de categorías del menú</div>
        </div>
        <input
          className="cat-input"
          placeholder="Buscar..."
          value={filter}
          onChange={(e)=>setFilter(e.target.value)}
          style={{ maxWidth: 260 }}
        />
      </div>

      {isAdmin && (
        <div className="ui-card" style={{ maxWidth: 560 }}>
          <h3 style={{ marginTop:0 }}>Nueva categoría</h3>
          <form className="cat-form" onSubmit={onCreate}>
            <div>
              <label style={{ display:"block", fontSize:12, marginBottom:6 }}>Nombre</label>
              <input className="cat-input" value={form.nombre} onChange={(e)=>setForm(f=>({...f, nombre:e.target.value}))} />
            </div>
            <div>
              <label style={{ display:"block", fontSize:12, marginBottom:6 }}>Descripción (opcional)</label>
              <textarea className="cat-textarea" value={form.descripcion} onChange={(e)=>setForm(f=>({...f, descripcion:e.target.value}))} />
            </div>
            <div style={{ display:"flex", gap:8, justifyContent:"flex-end" }}>
              <button className="btn btn-ghost" type="button" onClick={()=>setForm({nombre:"", descripcion:""})}>Limpiar</button>
              <button className="btn btn-primary" disabled={creating} type="submit">Guardar</button>
            </div>
          </form>
        </div>
      )}

      <div className="cat-table">
        <table className="cat-table">
          <thead>
            <tr>
              <th style={{ width: 64 }}>ID</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th style={{ width: 120 }}>Estado</th>
              {isAdmin && <th style={{ width: 200 }}>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={isAdmin ? 5 : 4} style={{ padding:16, textAlign:"center", color:"var(--muted)" }}>Sin resultados</td></tr>
            )}

            {filtered.map(row => (
              <tr key={row.id_categoria}>
                <td>{row.id_categoria}</td>
                <td>
                  {isAdmin ? (
                    <InlineText
                      value={row.nombre}
                      onSave={(v)=> onInlineEdit(row.id_categoria, { nombre: v })}
                    />
                  ) : row.nombre}
                </td>
                <td>
                  {isAdmin ? (
                    <InlineText
                      value={row.descripcion || ""}
                      placeholder="Sin descripción"
                      onSave={(v)=> onInlineEdit(row.id_categoria, { descripcion: v || null })}
                    />
                  ) : (row.descripcion || <span className="subtle">—</span>)}
                </td>
                <td>
                  <span className={`cat-badge ${row.activo ? "ok":"off"}`}>
                    {row.activo ? "Activo" : "Inactivo"}
                  </span>
                </td>
                {isAdmin && (
                  <td className="cat-actions">
                    <button
                      className="btn btn-ghost"
                      onClick={() => onToggle(row.id_categoria, row.activo)}
                    >
                      {row.activo ? "Desactivar" : "Activar"}
                    </button>

                    <button
                      className="btn btn-ghost"
                      onClick={async () => {
                        if (!confirm(`¿Seguro que deseas eliminar la categoría "${row.nombre}"?`)) {
                          return;
                        }
                        await deleteCategoria(row.id_categoria);
                        setItems((prev) =>
                          prev.filter((x) => x.id_categoria !== row.id_categoria)
                        );
                      }}
                    >
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {loading && <div className="subtle">Cargando...</div>}
    </div>
  );
}

/** Campo de texto “inline edit” simple */
function InlineText({
  value,
  onSave,
  placeholder,
}: {
  value: string;
  placeholder?: string;
  onSave: (val: string) => void;
}) {
  const [v, setV] = useState(value);
  const [editing, setEditing] = useState(false);

  useEffect(()=>setV(value), [value]);

  function commit(){
    setEditing(false);
    if(v !== value) onSave(v.trim());
  }

  return (
    <div>
      {editing ? (
        <input
          className="cat-input"
          value={v}
          placeholder={placeholder}
          onChange={(e)=>setV(e.target.value)}
          onBlur={commit}
          onKeyDown={(e)=>{ if(e.key==='Enter') commit(); if(e.key==='Escape'){ setV(value); setEditing(false); } }}
          autoFocus
          style={{ height: 34 }}
        />
      ) : (
        <span onDoubleClick={()=>setEditing(true)} style={{ cursor: "text" }}>
          {value || <span className="subtle">{placeholder || "—"}</span>}
        </span>
      )}
    </div>
  );
}
