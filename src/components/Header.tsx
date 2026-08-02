import { assets } from "../assets";
import { navItems } from "../content";

interface HeaderProps {
  isScrolled: boolean;
}

export function Header({ isScrolled }: HeaderProps) {
  const headerClassName = isScrolled ? "site-header is-scrolled" : "site-header";

  return (
    <header className={headerClassName}>
      <div className="container header-grid">
        <a className="brand-mark" href="#top" title="Abíádé home" aria-label="Abíádé home">
          <img src={assets.logo} alt="Abíádé" width="302" height="84" />
        </a>

        <nav className="primary-nav" aria-label="Primary navigation">
          {navItems.map(function renderNavItem(item) {
            return (
              <a key={item.href} href={item.href} title={item.title}>
                {item.label}
              </a>
            );
          })}
        </nav>

        <div className="header-actions">
          <a className="text-link" href="https://www.instagram.com/abiadeadire/" target="_blank" rel="noopener noreferrer" title="Open Abíádé on Instagram">
            Instagram
          </a>
          <a className="button button--light" href="#orders" title="View Abíádé Adire Festival tickets">
            Buy Tickets
          </a>
        </div>
      </div>
    </header>
  );
}
