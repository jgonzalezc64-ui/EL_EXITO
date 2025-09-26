import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "../components/Layout";
import LoginPage from "../pages/seguridad/LoginPage";
import { RequireAuth } from "./guards";

// Página de Categorías
import CategoriasPage from "../pages/catalogos/CategoriasPage";

export default function AppRouter() {
  return (
    <Routes>
      {/* Público */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protegido */}
      <Route element={<RequireAuth />}>
        <Route element={<Layout />}>
          {/* Al entrar al root, redirige a categorías */}
          <Route index element={<Navigate to="/catalogos/categorias" replace />} />

          {/* Catálogos */}
          <Route path="catalogos">
            <Route index element={<Navigate to="categorias" replace />} />
            <Route path="categorias" element={<CategoriasPage />} />
          </Route>
        </Route>
      </Route>

      {/* Cualquier otra ruta → login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
