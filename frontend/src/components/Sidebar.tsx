import React from 'react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Overview', icon: '◈' },
  { path: '/research', label: 'Research AI', icon: '⬡' },
  { path: '/sources', label: 'Sources', icon: '▣' },
  { path: '/analysis', label: 'Analysis', icon: '◎' },
  { path: '/comparison', label: 'Comparison', icon: '⊞' },
  { path: '/themes', label: 'Themes', icon: '◇' },

];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-row">
          <span className="brand-icon">E</span>
          <h1>ExpertLens</h1>
        </div>
        <p>Expert Interview Intelligence</p>
      </div>
      <nav className="sidebar-nav">
        <span className="nav-label">Navigation</span>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={item.path === '/'}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
