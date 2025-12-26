import React from "react";

export function Card({ title, subtitle, icon, children, footer }) {
  return (
    <section className="card">
      {(title || subtitle || icon) && (
        <header className="cardHeader">
          {icon && <div className="cardIcon">{icon}</div>}
          <div className="cardHeading">
            {title && <div className="cardTitle">{title}</div>}
            {subtitle && <div className="cardSubtitle">{subtitle}</div>}
          </div>
        </header>
      )}
      <div className="cardBody">{children}</div>
      {footer && <footer className="cardFooter">{footer}</footer>}
    </section>
  );
}

export function Button({ variant = "primary", className = "", ...props }) {
  return <button className={`btn btn-${variant} ${className}`.trim()} {...props} />;
}

export function Input({ label, hint, ...props }) {
  return (
    <label className="field">
      <span className="fieldLabel">{label}</span>
      <input className="input" {...props} />
      {hint && <span className="fieldHint">{hint}</span>}
    </label>
  );
}

export function Select({ label, children, ...props }) {
  return (
    <label className="field">
      <span className="fieldLabel">{label}</span>
      <select className="input" {...props}>
        {children}
      </select>
    </label>
  );
}

export function Textarea({ label, hint, ...props }) {
  return (
    <label className="field">
      <span className="fieldLabel">{label}</span>
      <textarea className="input textarea" {...props} />
      {hint && <span className="fieldHint">{hint}</span>}
    </label>
  );
}

export function Pill({ children }) {
  return <span className="pill">{children}</span>;
}

export function Divider() {
  return <div className="divider" role="separator" />;
}
