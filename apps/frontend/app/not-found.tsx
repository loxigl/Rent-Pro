import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Страница не найдена",
  description: "Запрашиваемая страница не найдена",
};

/**
 * Страница "Не найдено" (404)
 */
export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-6 py-24">
      <h1 className="text-6xl md:text-9xl font-bold text-primary-700 mb-4">404</h1>

      <h2 className="text-2xl md:text-3xl font-semibold mb-6 text-center">
        Страница не найдена
      </h2>

      <p className="text-lg text-secondary-600 max-w-md text-center mb-8">
        Возможно, страница была удалена, перемещена, или вы перешли по неверной ссылке.
      </p>

      <div className="flex flex-col sm:flex-row gap-4">
        <Link href="/">
          <Button size="lg">
            На главную
          </Button>
        </Link>

        <Link href="/catalog">
          <Button size="lg" variant="secondary">
            Перейти в каталог
          </Button>
        </Link>
      </div>
    </div>
  );
}