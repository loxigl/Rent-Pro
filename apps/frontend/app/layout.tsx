import type {Metadata} from "next";
import {Inter} from "next/font/google";
import "@/styles/globals.css";
import Link from "next/link";
import {ToastProvider} from "@/components/ui/toast";
// Настройка шрифта Inter
const inter = Inter({
    subsets: ["latin", "cyrillic"],
    display: "swap",
    variable: "--font-inter",
});

// Метаданные для всего сайта
export const metadata: Metadata = {
    title: {
        default: "Квартиры26 - Аренда квартир в Невинномысске",
        template: "%s | Квартиры26",
    },
    metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'),
    description: "Сервис аренды квартир в Невинномысске. Удобный поиск, актуальные предложения, быстрое бронирование.",
    keywords: ["аренда", "квартиры", "Невинномысск", "посуточно", "жилье"],
    authors: [{name: "Квартиры26 Team"}],
    creator: "Квартиры26",
    publisher: "Квартиры26",
    formatDetection: {
        email: false,
        address: false,
        telephone: false,
    },
    openGraph: {
        type: "website",
        locale: "ru_RU",
        siteName: "Квартиры26",
        title: "Квартиры26 - Аренда квартир в Невинномысске",
        description: "Сервис аренды квартир в Невинномысске. Удобный поиск, актуальные предложения, быстрое бронирование.",
        images: [
            {
                url: "/images/og-image.jpg",
                width: 1200,
                height: 630,
                alt: "Квартиры26",
            },
        ],
    },
};


export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ru" className={inter.variable}>
        <body className="min-h-screen flex flex-col">
        <ToastProvider>
            <header className="border-b border-secondary-200">
                <div className="container-custom py-4 flex justify-between items-center">
                    <Link href="/" className="text-xl font-bold text-primary-700">
                        Квартиры26
                    </Link>

                    <nav>
                        <ul className="flex gap-6">
                            <li>
                                <Link
                                    href="/catalog"
                                    className="text-secondary-700 hover:text-primary-600 transition-colors"
                                >
                                    Каталог
                                </Link>
                            </li>
                        </ul>
                    </nav>
                </div>
            </header>

            <main className="flex-1">{children}</main>

            <footer className="bg-secondary-900 text-white py-8">
                <div className="container-custom">
                    <div className="flex flex-col md:flex-row justify-between">
                        <div>
                            <div className="text-xl font-bold mb-4">Квартиры26</div>
                            <p className="text-secondary-300 max-w-md">
                                Удобный сервис аренды квартир в Невинномысске.
                                Актуальные предложения, быстрое бронирование, отзывчивая поддержка.
                            </p>
                        </div>

                        <div className="mt-6 md:mt-0">
                            <h3 className="text-lg font-semibold mb-4">Контакты</h3>
                            <ul className="space-y-2 text-secondary-300">
                                <li>Телефон: +7 (928) 320-90-83</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-8 pt-4 border-t border-secondary-700 text-center text-secondary-400 text-sm">
                        © {new Date().getFullYear()} Квартиры26. Все права защищены.
                    </div>
                </div>
            </footer>
        </ToastProvider>
        </body>
        </html>
    );
}