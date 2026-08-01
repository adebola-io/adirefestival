import { orderItems } from "../content";

export function Orders() {
  return (
    <section className="orders section-light motion-section" id="orders" aria-labelledby="orders-title" data-motion-section>
      <div className="container section-heading section-heading--split scroll-reveal">
        <div>
          <p className="eyebrow">
            TICKETS · <time dateTime="2026-12-26">DECEMBER 26</time>
          </p>
          <h2 id="orders-title">CHOOSE YOUR TICKET</h2>
        </div>
        <p>
          Select a ticket category for the <time dateTime="2026-12-26">December 26</time> festival. Each ticket opens its secure Paystack purchase page.
        </p>
      </div>

      <ol className="container order-grid scroll-reveal" aria-label="Abiade Adire Festival ticket categories">
        {orderItems.map(function renderOrderItem(item) {
          return (
            <li className="ticket-card" key={item.step}>
              <span className="ticket-card__number">{item.step}</span>
              <div className="ticket-card__copy">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
              <a className="button button--accent ticket-card__button" href={item.href} target="_blank" rel="noopener noreferrer" title={item.linkTitle}>
                Purchase Ticket
              </a>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
