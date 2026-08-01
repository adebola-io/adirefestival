import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { PreviewDialog } from "./components/PreviewDialog";
import { PromoBanner } from "./components/PromoBanner";
import { useHeaderScroll } from "./hooks/useHeaderScroll";
import { useLookbookPreview } from "./hooks/useLookbookPreview";
import { useMotionSections } from "./hooks/useMotionSections";
import { Contact } from "./sections/Contact";
import { Craft } from "./sections/Craft";
import { Hero } from "./sections/Hero";
import { Lookbook } from "./sections/Lookbook";
import { Orders } from "./sections/Orders";
import { PatternSection } from "./sections/PatternSection";
import { ProfessionalSeries } from "./sections/ProfessionalSeries";

export default function App() {
  useMotionSections();

  const isScrolled = useHeaderScroll();
  const { closePreview, handlePreviewBackdropClick, handlePreviewCancel, openPreview, previewDialogRef, previewItem } = useLookbookPreview();

  return (
    <>
      <a className="skip-link" href="#main" title="Skip to page content">
        Skip to content
      </a>

      <Header isScrolled={isScrolled} />

      <main id="main">
        <PromoBanner />
        <Hero />
        <PatternSection />
        <ProfessionalSeries />
        <Lookbook onPreview={openPreview} />
        <Craft />
        <Orders />
        <Contact />
      </main>

      <Footer />

      <PreviewDialog dialogRef={previewDialogRef} item={previewItem} onBackdropClick={handlePreviewBackdropClick} onCancel={handlePreviewCancel} onClose={closePreview} />
    </>
  );
}
