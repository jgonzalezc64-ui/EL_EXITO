import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../app/useAuth";

type Item = {
  label: string;
  to: string;
  roles?: string[]; // si no se define => visible para cualquier autenticado
};

const ITEMS: Item[] = [
  // Catálogos: visible para todos los autenticados, pero el CRUD ya lo controla el backend (Admin escribe)
  { label: "Catálogos", to: "/catalogos/categorias" },
  // Pedidos: MESERO y ADMIN
  { label: "Pedidos", to: "/pedidos", roles: ["MESERO", "ADMIN"] },
  // KDS: COCINA, MESERO y ADMIN (MESERO solo lectura, lo controla el backend)
  { label: "KDS", to: "/kds", roles: ["COCINA", "MESERO", "ADMIN"] },
  // Pagos: CAJA y ADMIN
  { label: "Pagos", to: "/pagos", roles: ["CAJA", "ADMIN"] },
  // Menús: solo ADMIN
  { label: "Menús", to: "/menus", roles: ["ADMIN"] },
];

export default function Sidebar() {
  const { hasRole, loading, user } = useAuth();
  const { pathname } = useLocation();

  // Mientras carga el perfil, muestra un placeholder
  if (loading) {
    return (
      <aside style={{ width: 220, background: "var(--sidebar-bg)", borderRight: "1px solid var(--border)" }}>
        <div style={{ padding: 16 }}>Cargando…</div>
      </aside>
    );
  }

  // Si no hay usuario, no mostramos navegación (ya hay guards que redirigen a /login)
  if (!user) return null;

  const visibleItems = ITEMS.filter(it => {
    if (!it.roles || it.roles.length === 0) return true;
    return it.roles.some(r => hasRole(r));
  });

  return (
    <aside style={{
      width: 220,
      background: "var(--sidebar-bg)",
      borderRight: "1px solid var(--border)",
      display: "flex",
      flexDirection: "column",
      gap: 8
    }}>
      {/* Logo y marca */}
      <div style={{padding: "16px 16px 8px", display:"flex", alignItems:"center", gap:10}}>
        <img
          src="/logo_el_exito.jpg"  /* usa /logo_el%20_exito.jpg si no renombraste */
          alt="El Éxito"
          style={{ width: 44, height: 44, objectFit:"contain" }}
        />
        <div style={{fontWeight: 800, color:"var(--brand-red)", lineHeight:1}}>
          El Éxito
          <div style={{fontSize: 11, color:"var(--muted)", fontWeight:600}}>Refacciones</div>
        </div>
      </div>

      {/* Navegación */}
      <nav style={{ padding: "8px 8px 16px" }}>
        <ul style={{ listStyle: "none", padding: 0, margin: 0, display:"grid", gap:4 }}>
          {visibleItems.map((it) => {
            const active = pathname.startsWith(it.to);
            return (
              <li key={it.to}>
                <Link
                  to={it.to}
                  style={{
                    display:"block",
                    padding:"10px 12px",
                    borderRadius:10,
                    textDecoration:"none",
                    fontWeight:600,
                    color: active ? "var(--brand-white)" : "var(--text)",
                    background: active ? "var(--brand-red)" : "transparent",
                  }}
                >
                  {it.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
