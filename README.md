# 3D-Print Cost Calculator Pro

[🇺🇸 English version](README.md) | [🇩🇪 Deutsche Version](README.de.md)

**The professional complete solution for precise cost calculation and efficient management of your 3D printing projects.**

The 3D-Print Cost Calculator Pro was developed to bridge the gap between simple slicing and an economical overview. Whether for dedicated hobbyists or semi-professional users – this tool offers clear control over the actual cost factors involved in 3D printing.

---

## ✨ Main Features

### 1. Precise Cost Calculation & Pricing
*   **Holistic Calculation**: Consideration of material consumption, electricity costs, machine depreciation, maintenance costs, and labor time.
*   **Advanced Energy Costs**: Differentiated tracking of printer idle consumption, heated bed power, and heated chamber power.
*   **Filament Calibration**: Unique system for determining actual power consumption (Power Factor) per filament type for maximum accuracy.
*   **Profit Margin & Customer Tiers**: Flexible pricing through definable margins and labor time factors for different customer groups (Private, Friends, Business).

### 2. Comprehensive Database Management
*   **Printer Fleet**: Management of technical data, purchase price, and expected lifetime for automatic calculation of depreciation per hour.
*   **Material Stock**: Detailed material database including density, price per kg, and specific recommendations for drying and heated chamber usage.
*   **Drying Management**: Integration of drying equipment (including AMS support) into the electricity cost calculation.

### 3. Calculation Archive & Customer Assignment
*   **History & Archive**: Overview of all saved calculations with detailed cost breakdowns for later retrieval.
*   **Customer Assignment**: Store customer names and assign them to price tiers for personalized quotes.
*   **Notes**: Save specific hints or documentation for each calculation.

### 4. Maintenance & Servicing System
*   **Maintenance Log**: Logging of all repairs and maintenance per printer.
*   **Spare Parts & Labor Costs**: Tracking of material costs and labor hours for maintenance interventions to determine actual operating costs.

### 5. Modern Interface & Technology
*   **Premium Design**: State-of-the-art UI with native Dark and Light modes, customizable accent colors, and smooth micro-animations.
*   **PWA Support**: Full installation as an app on mobile devices with an optimized, grid-based view.
*   **Global Localization**: Support for 22 languages with a dynamic translation system for all UI elements and metadata.

---

## 🛠️ Technology Stack

*   **Backend**: Python 3.10+ with [FastAPI](https://fastapi.tiangolo.com/) (High-performance web framework)
*   **Database**: [PostgreSQL](https://www.postgresql.org/) (Secure and scalable data storage)
*   **Frontend**: Modern Vanilla JavaScript (ES6+), HTML5, and flexible CSS3 (No heavy frameworks for maximum speed)
*   **Icons**: [Tabler Icons](https://tabler-icons.io/) for clear, technical symbolism
*   **Containerization**: [Docker](https://www.docker.com/) & Docker Compose for easy deployment

---

## ⚡ Quick Start

The fastest way to start the system is via Docker Compose:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ExtrudeEmpty/3d-print-cost-calculator.git
   cd 3d-print-cost-calculator
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   Open `http://<your-ip>` (or `http://localhost` for local installation) in your browser. (Default port: 80)

*Note: The database is automatically initialized and migrated on the first start.*

---

## 📚 Documentation & Contributing

For detailed guides on installation, API documentation, and troubleshooting, please see our [Full Documentation](docs/INDEX.md).

Want to contribute? We value your help! Please see our [Contribution Guidelines](CONTRIBUTING.md) for more information.

---

## ⚖️ License & Copyright

This project is licensed under the **GNU Affero General Public License v3 (AGPL-3.0)**.

**Copyright (c) 2026 ExtrudeEmpty**. All rights reserved.

**Credits**:
*   Icons from [Tabler Icons](https://tabler-icons.io/) (MIT License).

---

## 🎬 Behind the Scenes (The Making-of)

This project is the result of a fairly modern collaboration:
*   **Screenplay & Direction**: A real human, who pursued a clear vision (and wore out several whips in the process – whether due to the occasional slow-wittedness of the AIs or the challenge of translating complex visions into binary logic).
*   **Cast (Code)**: An ensemble of AIs (mainly **Gemini** and **Claude**), who typed away while living on vast amounts of virtual coffee and electricity.

Don't worry, no AIs were permanently harmed in the writing of this code – even if they sometimes needed three (or ten) attempts to finally place a button where the creator intended it.

---
*Developed with ❤️ and a pinch of AI madness for the 3D printing community.*
