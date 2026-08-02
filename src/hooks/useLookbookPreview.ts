import { useEffect, useRef, useState, type MouseEvent, type RefObject, type SyntheticEvent } from "react";
import type { LookbookItem, PreviewHandler } from "../types";

interface LookbookPreviewState {
  closePreview: () => void;
  handlePreviewBackdropClick: (event: MouseEvent<HTMLDialogElement>) => void;
  handlePreviewCancel: (event: SyntheticEvent<HTMLDialogElement, Event>) => void;
  openPreview: PreviewHandler;
  previewDialogRef: RefObject<HTMLDialogElement | null>;
  previewItem: LookbookItem | null;
}

export function useLookbookPreview(): LookbookPreviewState {
  const [previewItem, setPreviewItem] = useState<LookbookItem | null>(null);
  const previewDialogRef = useRef<HTMLDialogElement>(null);
  const lastPreviewTriggerRef = useRef<HTMLButtonElement>(null);

  useEffect(
    function syncScrollLock() {
      const shouldLock = Boolean(previewItem);
      document.documentElement.classList.toggle("is-scroll-locked", shouldLock);

      return function cleanupScrollLock() {
        document.documentElement.classList.remove("is-scroll-locked");
      };
    },
    [previewItem]
  );

  useEffect(
    function syncPreviewDialog() {
      const dialog = previewDialogRef.current;

      if (!dialog) {
        return;
      }

      if (previewItem && !dialog.open) {
        dialog.showModal();
        return;
      }

      if (!previewItem && dialog.open) {
        dialog.close();
      }
    },
    [previewItem]
  );

  function openPreview(item: LookbookItem, event: MouseEvent<HTMLButtonElement>) {
    lastPreviewTriggerRef.current = event.currentTarget;
    setPreviewItem(item);
  }

  function closePreview() {
    setPreviewItem(null);
    lastPreviewTriggerRef.current?.focus();
    lastPreviewTriggerRef.current = null;
  }

  function handlePreviewCancel(event: SyntheticEvent<HTMLDialogElement, Event>) {
    event.preventDefault();
    closePreview();
  }

  function handlePreviewBackdropClick(event: MouseEvent<HTMLDialogElement>) {
    if (event.target !== event.currentTarget) {
      return;
    }

    closePreview();
  }

  return { closePreview, handlePreviewBackdropClick, handlePreviewCancel, openPreview, previewDialogRef, previewItem };
}
