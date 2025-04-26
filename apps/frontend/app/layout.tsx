import type {Metadata} from "next";
import {Inter} from "next/font/google";
import "@/styles/globals.css";
import Link from "next/link";

// Настройка шрифта Inter
const inter = Inter({
    subsets: ["latin", "cyrillic"],
    display: "swap",
    variable: "--font-inter",
});

// Метаданные для всего сайта
export const metadata: Metadata = {
    title: {
        default: "AvitoRentPro - Аренда квартир в Невинномысске",
        template: "%s | AvitoRentPro",
    },
    description: "Сервис аренды квартир в Невинномысске. Удобный поиск, актуальные предложения, быстрое бронирование.",
    keywords: ["аренда", "квартиры", "Невинномысск", "посуточно", "жилье"],
    authors: [{name: "AvitoRentPro Team"}],
    creator: "AvitoRentPro",
    publisher: "AvitoRentPro",
    formatDetection: {
        email: false,
        address: false,
        telephone: false,
    },
    openGraph: {
        type: "website",
        locale: "ru_RU",
        siteName: "AvitoRentPro",
        title: "AvitoRentPro - Аренда квартир в Невинномысске",
        description: "Сервис аренды квартир в Невинномысске. Удобный поиск, актуальные предложения, быстрое бронирование.",
        images: [
            {
                url: "/images/og-image.jpg",
                width: 1200,
                height: 630,
                alt: "AvitoRentPro",
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
        <header className="border-b border-secondary-200">
            <div className="container-custom py-4 flex justify-between items-center">
                <Link href="/" className="text-xl font-bold text-primary-700">
                    AvitoRentPro
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
                        <div className="text-xl font-bold mb-4">AvitoRentPro</div>
                        <p className="text-secondary-300 max-w-md">
                            Удобный сервис аренды квартир в Невинномысске.
                            Актуальные предложения, быстрое бронирование, отзывчивая поддержка.
                        </p>
                    </div>

                    <div className="mt-6 md:mt-0">
                        <h3 className="text-lg font-semibold mb-4">Контакты</h3>
                        <ul className="space-y-2 text-secondary-300">
                            <li>Телефон: +7 (999) 123-45-67</li>
                            <li>Email: info@avitorentpro.ru</li>
                            <li>Адрес: г. Невинномысск, ул. Ленина, 1</li>
                        </ul>
                    </div>
                </div>

                <div className="mt-8 pt-4 border-t border-secondary-700 text-center text-secondary-400 text-sm">
                    © {new Date().getFullYear()} AvitoRentPro. Все права защищены.
                </div>
            </div>
        </footer>
        </body>
        </html>
    );
}