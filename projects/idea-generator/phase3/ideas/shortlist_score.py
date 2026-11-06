#!/usr/bin/env python3
"""T12 quick scoring: weighted scores, bands and shortlist for the 95 longlist ideas.

Run from anywhere:  python3 shortlist_score.py
Reads nothing; the quick scores below are judgments from the T04-T11 files
(see longlist.md for the evidence of each idea). Writes shortlist.csv next to
this file and prints the rejected list grouped by reason (pasted into
../rejected.md). Weights and band rules: ../method/criteria.md.
"""

import csv
import os

WEIGHTS = [0.15, 0.15, 0.10, 0.15, 0.10, 0.12, 0.08, 0.08, 0.07]  # F1..F9

L = "longlist.md"
SEC = {
    "V1": L + "#v1--vehicle-parts-and-car-related-buying",
    "V2": L + "#v2--home-climate-and-appliance-parts-and-consumables",
    "V3": L + "#v3--hobby-niches-with-thin-coverage",
    "V4": L + "#v4--services-with-a-logistics-step",
    "V5": L + "#v5--small-business-and-professional-buying",
}

# idea: (short name, vertical, owner area, main model, scores F1..F9, T10 result,
#        decision, reason)
# decision: "S" = shortlist; otherwise a reject group key (see REJECT_GROUPS).
IDEAS = {
    1: ("Collision-part sourcing desk for Chinese brands", "V1", "car", "service fee", "523325323", "N/W", "S",
        "T10 not found; owners wait months for body parts (V1 demand S3) but the parts sit with importers, so a desk can only chase them"),
    2: ("Aftermarket cross-reference for Chinese-brand service parts", "V1", "car", "commission", "433233233", "N/W", "S",
        "T10 not found for Jaecoo pads; value is an OE-to-aftermarket table that grows with the fleet; brake pads make fit claims risky"),
    3: ("Group order of Chinese-brand parts direct from China", "V1", "car", "margin", "324323212", "N", "KO",
        "founder becomes importer of record (customs, GPSR, paying ahead for a group): stock-like risk and capital"),
    4: ("Tesla parts route", "V1", "car", "commission", "112221232", "E", "INC",
        "T10 found many Polish shops on Ceneo in one try"),
    5: ("US-import car parts with specialist map", "V1", "car", "lead fee", "222221332", "E", "INC",
        "T10 found several shops; local specialists already searched by city"),
    6: ("Parts locator for discontinued brands (Saab)", "V1", "car", "commission", "121221332", "E", "INC",
        "T10 found many shops on Ceneo for the Saab item"),
    7: ("Condition-graded NOS marketplace for classic Polish cars", "V1", "car", "commission", "323233433", "W", "LOW",
        "commission on 100-300 zl parts cannot pay for condition grading; channel unverified (band <5%)"),
    8: ("Camper habitation parts by body brand, dropshipped from DE", "V1", "car", "margin", "433334333", "N/W", "S",
        "T10 not found for the Knaus seal and one OLX seller for Hymer glass; German camper suppliers exist; owner area"),
    9: ("Parts finder for Polish and UK-built caravans", "V1", "car", "commission", "322223332", "W", "MERGE8",
        "merged into #8 (same buyers and channel); the maker niewiadow.pl still runs a shop"),
    10: ("Camper mirror and window fit checker", "V1", "car", "commission", "322223342", "W", "MERGE8",
         "merged into #8; on its own a commission on a few mirrors a month"),
    11: ("Van-conversion component kits from DE/US makers", "V1", "car", "margin", "432324332", "N", "S",
         "sliding windows not found in Poland (T10 N); high ticket; bulky glass shipped cross-border"),
    12: ("Chinese quad/ATV parts by exact model", "V1", "car", "margin", "323233333", "N/E", "LOW",
        "gap is uneven by brand (Bashan parts found easily, Linhai only on eBay.de); low ticket (band <5%)"),
    13: ("Chinese scooter parts by engine type", "V1", "car", "commission", "232222332", "not tested", "UNTESTED",
         "not tested; the nearest item (Bashan quad parts) was found easily"),
    14: ("Genuine OE parts outside the dealer", "V1", "car", "commission", "121221332", "E", "INC",
         "T10 found the Toyota filter in 2 shops at once"),
    15: ("Garage price comparison and booking around the yearly inspection", "V1", "", "lead fee", "334222332", "not tested", "LOW",
        "booking earns little (iDGARAGES ~EUR 36 per booking, V1 scan 8); Dobry Mechanik and Motointegrator partly cover it; garages unlikely to publish prices (band <5%)"),
    16: ("Car collection and return for servicing", "V1", "", "service fee", "323221312", "not tested", "KO",
         "drivers and insurance are physical work far above 8 h/month (F8 = 1); Flovi already in Poland"),
    17: ("Photo-based body-damage quote to partner body shops", "V1", "", "lead fee", "434344333", "not tested", "S",
         "no photo-quote service found in Poland and quotes for the same damage differ by 100% (V1 scan 6); body shops do the work"),
    18: ("Fair-price repair estimate honoured by garages", "V1", "", "lead fee", "323223323", "not tested", "LOW",
        "needs licensed labour-time data and garages that guarantee a price; same weak booking economics as #15"),
    19: ("Fitment data for Allegro and Shoper parts sellers", "V1", "car", "subscription", "334343333", "not tested", "S",
         "about 48 m Allegro motoring offers lack VIN fit (V1 scan 4); Partly and Versable show buyers pay for fit data"),
    20: ("One search across parts wholesalers for workshops", "V1", "car", "subscription", "234322423", "not tested", "LOW",
         "workshops already use Inter Cars and Auto Partner portals; API access unverified; slow B2B sales (V1 scan 8)"),
    21: ("Wallbox installation booking", "V1", "", "lead fee", "224312432", "not tested", "LOW",
         "Oferteo and Fixly already sell installer leads; little AI role; EV fleet size not sourced"),
    22: ("Used-parts marketplace for one niche on dismantler stock", "V1", "car", "commission", "223322322", "not tested", "LOW",
         "Ovoko already serves used parts in Polish; niche dismantler supply unverified"),
    23: ("Odd-size camper and trailer tyre finder", "V1", "car", "commission", "122211342", "E", "INC",
         "T10 found the tyre in several shops; Oponeo has ~1,100 fitting points"),
    24: ("Spare parts for distributor-only heat-pump brands, for installers", "V2", "HVAC", "margin", "433334333", "N", "S",
         "T10 found units but no spare parts for Kaisai; KLIMA-THERM is the distributor; installers buy repeatedly"),
    25: ("AC replacement remote by remote code and unit model", "V2", "HVAC", "margin", "333232442", "E/N", "LOW",
        "Kaisai remote not found but Gree easy (T10); low ticket against generic remotes on Allegro; keep as an entry product for #24"),
    26: ("AC unit spare parts by indoor-unit model, for installers", "V2", "HVAC", "margin", "333333333", "not tested", "MERGE24",
         "merged into #24 (same installers, same distributors); only remotes were tested"),
    27: ("Yearly AC cleaning and service booking with a spring reminder", "V2", "HVAC", "lead fee", "234222333", "E (pricing)", "LOW",
         "AC installation pricing found easily (T10 V4 #19); Oferteo and Fixly hold installer leads; booking fee small"),
    28: ("Heat-pump installer comparison that files Czyste Powietrze paperwork", "V2", "HVAC", "lead fee", "334332322", "not tested", "S",
         "no service found that also files the subsidy paperwork (V2 scan 6); Enerad and Pompy.app compare; Woltair died with subsidies"),
    29: ("Fixed online price for a boiler or heat-pump swap", "V2", "HVAC", "margin", "333221311", "not tested", "KO",
         "founder carries the job risk and needs finance and installer capacity (F8 = 1, BOXT pattern needs capital)"),
    30: ("MVHR (rekuperator) filter subscription by unit model", "V2", "HVAC", "subscription", "233322443", "E", "S",
         "filters are easy to find (T10 E) so the value is the reminder and the exact set; recurring 2-4 times a year"),
    31: ("Air-purifier and water-jug filter subscription with a fit table", "V2", "", "subscription", "233222442", "E", "LOW",
         "T10 found the filter easily; low value per parcel against Allegro Smart! free delivery (PLN 59.90/year)"),
    32: ("Fridge water filters, originals vs clones", "V2", "", "margin", "123121332", "E", "INC",
         "T10 found the Samsung filter in many shops"),
    33: ("Fit-checked used modules for discontinued washers from donor machines", "V2", "", "commission", "433334333", "W/N", "S",
         "no wholesaler for old modules (T10 W/N); repairers and elektroda forum hold the supply and the questions"),
    34: ("Drum spiders and bearing kits from German parts shops", "V2", "", "margin", "423223342", "N", "MERGE36",
         "merged into #36 as one of the parts the diagnosis flow sells; on its own a rare purchase"),
    35: ("Control boards for store-brand cooker hoods", "V2", "", "margin", "421122332", "N", "LOW",
         "a whole new hood costs from 49 zl (T10), so a board is rarely worth buying (F4 = 1)"),
    36: ("Video or photo diagnosis before the part, ending in a dropshipped part", "V2", "", "service fee + margin", "433344333", "W/N", "S",
         "no Polish video-diagnosis service (V2 scan 6); Spareka converts ~30% of guided customers to a part; CzęściAGD.pl also wholesales"),
    37: ("Rating-plate photo to part number, widget for appliance-parts shops", "V2", "", "subscription", "324343333", "not tested", "S",
         "B2B tool where the AI step is the product; few buyers (parts shops), so F2 is low"),
    38: ("Fridge door gasket lookup by fridge model", "V2", "", "margin", "333233342", "W", "MERGE36",
         "merged into #36 (model-to-part lookup is one step of the same flow); found by part number only (T10 W)"),
    39: ("Cordless-tool battery cross-compatibility guide", "V2", "", "commission", "132111342", "E", "INC",
         "T10 found Parkside batteries in several shops"),
    40: ("Coal and pellet boiler parts by boiler model", "V2", "", "margin", "132221332", "E", "INC",
         "T10 found the Defro controller in several shops"),
    41: ("Robot and cordless vacuum parts by model", "V2", "", "commission", "132111342", "E", "INC",
         "T10 found the Dyson V11 battery in many shops"),
    42: ("Kitchen-robot spare parts by model", "V2", "", "commission", "132111342", "E", "INC",
         "T10 found all three kitchen-robot items easily"),
    43: ("Gas-cooker parts by brand", "V2", "", "commission", "132111232", "E", "INC",
         "T10 found the Amica thermocouple easily; gas fit claims are a liability"),
    44: ("Coffee-machine consumables replenishment", "V2", "", "subscription", "131211343", "not tested", "INC",
         "Coffee Friend already sells in Poland (coffeefriend.pl, przyjacielekawy.pl)"),
    45: ("Cross-brand vacuum-bag fit table", "V2", "", "commission", "232131342", "not tested", "LOW",
         "low order value; Swirl and generic bags on Allegro and Kaufland; affiliate per bag pack is a few zloty (F4 = 1)"),
    46: ("Parts and battery-health check for imported Dutch e-bikes", "V3", "hobby", "margin + fee", "332332223", "W", "LOW",
        "used batteries sold with unknown health (T10 W), but lithium shipping rules are not checked and the e-bike count is not sourced"),
    47: ("Fishing-reel spare parts by exploded-diagram code", "V3", "hobby", "margin", "333233433", "W", "S",
         "reel parts only from private sellers (T10 W); 500,000 PZW members (V3 scan 6) give the pool; small parts, low ticket"),
    48: ("Sewing-machine parts by model (Lucznik, Singer)", "V3", "hobby", "margin", "322223432", "W", "LOW",
         "only private ads with unclear fit (T10 W); no supplier beyond private sellers; low ticket"),
    49: ("Single LEGO parts in PLN pooling Polish sellers", "V3", "hobby", "commission", "233232432", "W", "LOW",
         "Brick Owl already shows PLN prices and BrickLink has the sellers (T10 W)"),
    50: ("Model-kit price and stock comparison across Polish and nearby shops", "V3", "hobby", "commission", "224233443", "E", "S",
         "named kits are easy to find but no Polish price comparison exists (V3 scan 7); affiliate pays little"),
    51: ("Polish-language proxy buying from Japan", "V3", "hobby", "service fee", "333322232", "E", "LOW",
         "Remambo and ZenMarket already serve Poland in English; import VAT handling puts customs liability on the founder"),
    52: ("Instant multi-bureau 3D-print quote from an uploaded file", "V3", "hobby", "commission", "334334443", "not tested", "S",
         "Polish bureaus quote each file by hand (Oferteo PLN 30-60 per machine hour); Craftcloud's routing model survived Shapeways"),
    53: ("Fishing subscription box for the PZW audience", "V3", "hobby", "subscription", "243324433", "not tested", "S",
         "no active Polish fishing box found (V3 scan 7); 500,000 PZW members; Catch Co.'s pandemic spike is the hype warning"),
    54: ("Escrow plus courier for used road bikes", "V3", "hobby", "commission", "332322232", "not tested", "LOW",
         "oversize bike shipping plus holding buyers' money (payment-service rules); OLX protected payment exists; buycycle may enter"),
    55: ("Mechanical-keyboard compatibility table with EU dropship", "V3", "hobby", "commission", "122231342", "E", "INC",
         "T10 found the switches in a Polish shop; group size unverified"),
    56: ("Aquarium-filter spare parts by model across brands", "V3", "hobby", "margin", "232232442", "not tested", "UNTESTED",
         "not tested; Aquael, the main Polish maker, already publishes a parts catalogue"),
    57: ("Shipping coordination for live aquarium stock", "V3", "hobby", "service fee", "222121332", "E", "INC",
         "T10 found shrimp locally with pick-up; legal species limits (S21)"),
    58: ("Available-now board for mated queen bees", "V3", "hobby", "lead fee", "333223443", "W", "S",
         "one od reki offer found (T10 W); 98,000 beekeepers (V3 scan 6) buy queens every season; live-animal shipping"),
    59: ("Ham-radio gear with EU stock and pick-up", "V3", "hobby", "commission", "112221332", "E", "INC",
         "T10 found the Yaesu radio at a Polish specialist; about 16,000 licences only"),
    60: ("Unitra turntable parts and styli fit lookup", "V3", "hobby", "commission", "122221342", "E", "INC",
         "T10 found the stylus in 2 small shops"),
    61: ("E-scooter parts by model", "V3", "hobby", "commission", "232222332", "not tested", "LOW",
        "not tested and no supplier named"),
    62: ("RC model parts finder across foreign sellers", "V3", "hobby", "commission", "312223332", "not tested", "UNTESTED",
         "not tested; group size unverified; supply is HobbyKing and Chinese sellers by inference only"),
    63: ("Model-railway parts from German and Czech makers", "V3", "hobby", "commission", "312223332", "not tested", "UNTESTED",
         "not tested; group size and makers (Roco, Piko) unverified"),
    64: ("Used and subsidy-eligible beekeeping equipment", "V3", "hobby", "commission", "122221332", "not tested", "INC",
         "domestic makers (Lyson) and many shops already serve beekeepers; friction is price only"),
    65: ("Mail-in smartwatch repair routed to partner technicians", "V4", "", "service fee", "433323332", "W/N", "S",
         "Huawei battery repair not found, Garmin only via one OLX technician (T10); partner does the repair, InPost both ways"),
    66: ("Mechanical-watch service by post through independent watchmakers", "V4", "", "service fee", "323323332", "W", "LOW",
         "brand centres exist (1-2 months wait, T10 W); independents unverified; valuable items in transit"),
    67: ("Down-jacket repair and refill by post", "V4", "", "service fee", "433324432", "N", "S",
         "no workshop found (T10 N); care repeat is real abroad (Clothes Doctor 3-4 orders a year, V4 scan 4); seasonal"),
    68: ("Clothing repair by post with a photo quote", "V4", "", "service fee", "233332432", "E", "MERGE67",
         "merged into #67: start with down jackets where T10 found the gap; zip repair is found locally (T10 E)"),
    69: ("Post-warranty repair by post for robot and cordless vacuums", "V4", "", "service fee", "333333332", "W/E", "S",
         "Roborock repair hard to find, Dyson easy (T10); fault triage from photos and logs is an AI step"),
    70: ("Thermomix post-warranty repair by post", "V4", "", "service fee", "322323332", "W", "LOW",
         "only Vorwerk's own service found and no independent repairer named (T10 W)"),
    71: ("Vintage audio and instrument repair directory with courier pick-up", "V4", "", "commission", "322223333", "W", "LOW",
         "single providers only (T10 W); fragile items, small group, low commission"),
    72: ("Car premium-audio module repair by post", "V4", "car", "service fee", "523324333", "N", "S",
         "only UK and US services found (T10 N); a module ships in a normal parcel; small group per module"),
    73: ("Camera-lens repair by post to independent repairers", "V4", "", "service fee", "322323332", "W", "LOW",
         "canon.pl runs send-in repair; independent repairers unverified"),
    74: ("E-bike battery cell replacement by post", "V4", "hobby", "service fee", "432323223", "W", "LOW",
        "one provider found (T10 W), but lithium shipping rules are unchecked and battery-fire liability is high (F7 = 2, band <5%)"),
    75: ("Knife and hairdressing-scissor sharpening by post", "V4", "", "service fee / subscription", "233213333", "W", "LOW",
         "local sharpeners from 30 zl; two-way postage eats most of the fee (F4 = 2); courier rules for blades not found"),
    76: ("Repair service sold to fashion and outdoor brands", "V4", "", "service fee (brand pays)", "223323433", "not tested", "LOW",
        "Polish brand count and tailor network unverified; the consumer side is covered by #67 (band <5%)"),
    77: ("Installation slot at checkout for Allegro and small-shop sellers", "V4", "", "service fee", "233222323", "not tested", "LOW",
         "Media Expert and Morele already sell installation in the basket; installers per city needed (F8 = 2)"),
    78: ("Dry cleaning through an InPost-locker round trip", "V4", "", "service fee", "233122322", "not tested", "LOW",
         "graveyard (Laundrapp, Zipjet) shows thin laundry margins (F4 = 1)"),
    79: ("E-scooter repair for small towns", "V4", "", "service fee", "332222322", "W", "LOW",
         "one mobile provider found (T10 W); scooters are heavy to post; local mechanics needed"),
    80: ("Shoe repair by courier with partner cobblers", "V4", "", "service fee", "223222332", "not tested", "UNTESTED",
         "not tested; woshwosh via Zabka already offers shoe repair drop-off"),
    81: ("Catering-equipment spare parts from EU distributors for restaurants", "V5", "", "margin", "533334433", "N", "S",
         "both Unox and Carpigiani parts only found abroad (T10 N); downtime makes restaurants pay; B2B invoices"),
    82: ("Parts for orphan and Chinese construction machinery", "V5", "", "margin", "422334323", "W/N", "LOW",
        "one Truck1 seller only; heavy parts and phone sourcing push physical work to the F8 limit"),
    83: ("Parts for old Eastern-bloc forklifts", "V5", "", "margin", "412324322", "W/N", "LOW",
         "a shrinking fleet and private-only supply (catalogues sold privately)"),
    84: ("Industrial sewing-machine parts for the Lodz textile cluster", "V5", "", "margin", "423334433", "N", "S",
         "machines listed but no parts (T10 N); Juki parts are standardised; supplier unverified"),
    85: ("Hydraulic-seal matcher by profile and size", "V5", "", "margin", "333233443", "W", "S",
         "size found but not the profile (T10 W); classifying a seal from photo and dimensions is a real AI step"),
    86: ("Farm-implement wear parts by dimension rather than brand", "V5", "", "margin", "333233433", "W", "LOW",
        "only one brand's tines found (T10 W), but farmers buy from local agri shops and tickets are low"),
    87: ("Ordering app between restaurants and their wholesalers", "V5", "", "subscription (supplier pays)", "334343423", "not tested", "S",
         "no Choco-like app found in Poland (V5 scan 6); supplier-paid subscription with daily use; slow B2B sales"),
    88: ("One checkout across dental distributors", "V5", "", "commission", "233323222", "not tested", "LOW",
         "distributor names not collected; medical-device rules unchecked; dental-unit parts only abroad (T10 N) is a different idea"),
    89: ("Cross-wholesaler reordering for salons", "V5", "", "commission", "233232433", "E", "INC",
         "T10 found at least 4 online hairdressing wholesalers with delivery and loyalty discounts"),
    90: ("Drop-ship MRO, workwear and safety catalogue for SMEs", "V5", "", "margin", "233322332", "not tested", "LOW",
         "XBHP and Allegro Biznes serve SMEs with VAT invoices; Mapudo shows horizontal B2B fails"),
    91: ("Instant laser-cutting quote from a CAD file to local job shops", "V5", "", "margin", "333433233", "not tested", "S",
         "Xometry holds ~33% marketplace margin (V5 scan 4); Polish check not done; quality liability if the founder is seller"),
    92: ("Builders'-merchant stock lookup with fast delivery to site", "V5", "", "service fee", "332222322", "not tested", "LOW",
         "courier coordination per order; merchant stock data unverified; Schuttflix shows logistics burns capital"),
    93: ("Procurement workflow for small contractors on TIM or Onninen", "V5", "", "subscription", "234322423", "not tested", "LOW",
         "TIM already sells about 70% online; long sales cycle for a 40 h/month founder"),
    94: ("Cash-register printing mechanisms outside authorised service", "V5", "", "margin", "422231232", "N", "REG",
         "fiscal cash registers are serviced by authorised service only (fiscal rules not checked): F7 = 1"),
    95: ("Plate-compactor and pressure-washer wear parts", "V5", "", "commission", "132221342", "E", "INC",
         "T10 found both items in shops on Ceneo"),
}

# Extra fields for shortlisted ideas: recurring?, top opportunity, top risk,
# first supplier, first channel, evidence links (relative to ideas/).
SHORT = {
    1: ("no", "fleet of new Chinese brands keeps growing and owners already organise in large groups (H/H)",
        "importers hold all stock, so the desk cannot shorten the wait (H/H)",
        "brand importers and dealers (ASO); used parts on OLX",
        "Omoda Polska Facebook group (>30,000 members, V1 demand S3)",
        "[V1 #2](../findability/V1-vehicle-parts.md#2-rear-bumper-omoda-5-v1-d01), [V1-D01](../demand/V1-vehicle-parts.md#candidate-hard-to-find-items-feeds-t10)"),
    2: ("yes: service parts (pads, filters) recur at each service",
        "first-mover cross-reference table for brands no wholesaler covers yet (M/H)",
        "wholesalers add the brands to TecDoc and Allegro VIN search covers them (H/M)",
        "unverified (no wholesaler stocks Jaecoo pads, V1 demand S5)",
        "Chinese-brand owners' Facebook groups (V1 demand S3)",
        "[V1 #1](../findability/V1-vehicle-parts.md#1-front-brake-pads-jaecoo-7-v1-d02), [V1 #3](../findability/V1-vehicle-parts.md#3-oil-filter-mg-zs-v1-d02)"),
    8: ("no", "German camper suppliers ship parts that Polish shops do not list (M/H)",
        "dropship terms from German suppliers unavailable to a newcomer (M/H)",
        "Reimo (seen in T10 item 7); Dometic windows via one OLX seller",
        "SEO on the camper-parts autocomplete phrases (V1-D07, 10 suggestions)",
        "[V1 #7](../findability/V1-vehicle-parts.md#7-entrance-door-seal-knaus-camper-v1-d07), [V1 #17](../findability/V1-vehicle-parts.md#17-window-glass-for-a-hymer-camper-v1-d07)"),
    11: ("no", "sliding windows only available from DE/US makers (M/M)",
         "bulky glass and cross-border returns make each order costly (H/M)",
         "Brandrup (DE) or Nomadic Supply (US); Reimo PL hinged only",
         "SEO on zabudowa busa phrases (V1-D14, 1 suggestion only)",
         "[V1 #16](../findability/V1-vehicle-parts.md#16-sliding-side-window-for-a-van-conversion-v1-d14)"),
    17: ("no", "body shops want qualified jobs and quotes vary by 100% (M/H)",
         "insurers and leasing firms steer most repairs, leaving few cash jobs (M/H)",
         "local body shops (none named; kb.pl price lists show them)",
         "unverified (cash-paying drivers after small damage; no channel named)",
         "[V1 scan 6](../research/verticals/V1-vehicle-parts.md#6-ten-most-promising-analogues-for-poland-quick-polish-check), [Fixico V1-NL-001](../catalogue/V1-vehicle-parts.csv)"),
    19: ("yes: sellers add listings every week and need fit data for each",
         "about 48 m Allegro motoring offers sit outside VIN search (H/H)",
         "TecDoc or OE data licence too costly or AI extraction not allowed (M/H)",
         "TecDoc or OE data licence, or AI extraction from listings (rights unverified)",
         "Allegro and Shoper parts sellers (none contacted)",
         "[V1 scan 4](../research/verticals/V1-vehicle-parts.md#4-what-the-numbers-say), [V1 scan 8](../research/verticals/V1-vehicle-parts.md#8-takeaways-for-t09t11)"),
    24: ("yes: installers order parts at every repair, and a parts subscription is possible",
         "distributor-only brands leave installers without a parts shop (M/H)",
         "KLIMA-THERM sells parts only to its own installer network (M/H)",
         "KLIMA-THERM (Kaisai distributor, T10)",
         "heat-pump installers searching the V2-D04 phrases (9 suggestions)",
         "[V2 #5](../findability/V2-home-climate-appliance.md#5-spare-parts-main-board-kaisai-heat-pump-v2-d04), [V2-D04](../demand/V2-home-climate-appliance.md#candidate-hard-to-find-items-feeds-t10)"),
    28: ("no", "subsidy paperwork is the step no comparison site does (M/H)",
         "subsidy cuts collapse demand, as with Woltair (M/H)",
         "installers with UDT / F-gas certificates (PORT PC guidance), none contacted",
         "unverified (Enerad and Pompy.app already hold comparison traffic)",
         "[V2 scan 6](../research/verticals/V2-home-climate-appliance.md#6-ten-most-promising-analogues-for-poland-quick-polish-check), [V2 scan 5](../research/verticals/V2-home-climate-appliance.md#5-graveyard-and-warnings)"),
    30: ("yes: MVHR filters must be changed 2-4 times a year and owners forget the exact set",
         "new houses with MVHR add owners who need the exact set every few months (M/M)",
         "buyers switch to cheap Ceneo offers once they know the code (H/M)",
         "unverified (Komfovent filters sold by >=4 shops on Ceneo; no dropship supplier named)",
         "SEO on filtr do rekuperatora phrases (V2-D06, 10 suggestions)",
         "[V2 #8](../findability/V2-home-climate-appliance.md#8-mvhr-filters-komfovent-domekt-r-450-v-v2-d06), [V2-D06](../demand/V2-home-climate-appliance.md#candidate-hard-to-find-items-feeds-t10)"),
    33: ("no", "repairers' donor machines are an untapped supply of tested modules (M/H)",
         "used modules fail and the returns cost more than the commission (M/M)",
         "independent repairers and OLX donor machines",
         "elektroda.pl forum threads on washer modules (V2-D01)",
         "[V2 #1](../findability/V2-home-climate-appliance.md#1-control-module-bosch-waw24540pl-washer-v2-d01), [V2 #3](../findability/V2-home-climate-appliance.md#3-programmer-module-electrolux-ewc-1350-v2-d01)"),
    36: ("no", "a diagnosis fee plus part margin per guided buyer, as Spareka shows (M/H)",
         "technician time per call eats the margin at Polish prices (M/H)",
         "CzęściAGD.pl (also a wholesaler); BSH shop by E-Nr",
         "SEO on co sie zepsulo w pralce type phrases (V2 scan 8)",
         "[V2 scan 6](../research/verticals/V2-home-climate-appliance.md#6-ten-most-promising-analogues-for-poland-quick-polish-check), [V2 scan 8](../research/verticals/V2-home-climate-appliance.md#8-takeaways-for-t09t11)"),
    37: ("yes: shops pay monthly for a widget that cuts wrong-part returns",
         "no live rating-plate-to-part tool seen in any V2 business (M/M)",
         "too few parts shops in Poland to reach 10,000 PLN a month (H/H)",
         "CzęściAGD.pl as a possible customer (unverified)",
         "direct sales to appliance-parts shops (none contacted)",
         "[T03 AI section](../research/global/friction-patterns.md#3-what-changes-with-cheap-ai), [V2 scan 4](../research/verticals/V2-home-climate-appliance.md#4-what-the-numbers-say)"),
    47: ("partly: reel parts wear out but rarely more than yearly",
         "Shimano diagram codes make an exact lookup possible (M/M)",
         "parts orders of 10-50 zl leave no margin after postage (H/M)",
         "Decathlon PL reel-parts category; private ads on Allegro Lokalnie",
         "PZW anglers (about 500,000 members, V3 scan 6); channel inside PZW unverified",
         "[V3 #7](../findability/V3-hobby-niches.md#7-bail-roller-shimano-spinning-reel-v3-d13), [V3-D13](../demand/V3-hobby-niches.md#candidate-hard-to-find-items-feeds-t10)"),
    50: ("no", "no Polish price comparison for model kits exists (M/M)",
         "shops refuse feeds and scraping terms forbid it (M/H)",
         "plastmodel.pl and other Polish shops (feed permission unverified)",
         "IPMS Polska and modelling festivals (V3 scan 6); reach unverified",
         "[V3 scan 7](../research/verticals/V3-hobby-niches.md#7-ten-most-promising-analogues-for-poland-quick-polish-check), [V3 #1](../findability/V3-hobby-niches.md#1-gunpla-kit-hg-1144-gundam-aerial-v3-d02)"),
    52: ("partly: firms and makers reorder prints", "firms and makers pay for an instant price instead of waiting for quotes (M/H)",
         "too few Polish bureaus agree to automatic pricing (M/H)",
         "Polish print bureaus quoting on Oferteo (none contacted)",
         "SEO on druk 3D na zamowienie cena (V3-D04)",
         "[V3 scan 7](../research/verticals/V3-hobby-niches.md#7-ten-most-promising-analogues-for-poland-quick-polish-check), [Craftcloud V3-DE-005](../catalogue/V3-hobby-niches.csv)"),
    53: ("yes: anglers fish all season and a monthly box gives new lures without shop trips",
         "500,000 PZW members and no active Polish box (H/M)",
         "boxes churn after a few months, as pandemic boxes did (H/H)",
         "unverified (no dropshipping lure wholesaler named)",
         "PZW angler groups (about 500,000 members, V3 scan 6); channel unverified",
         "[V3 scan 6](../research/verticals/V3-hobby-niches.md#6-hobbies-in-poland-size-and-supply-gap), [V3 scan 7](../research/verticals/V3-hobby-niches.md#7-ten-most-promising-analogues-for-poland-quick-polish-check)"),
    58: ("partly: beekeepers buy queens every season",
         "about 98,000 beekeepers look for queens in the same spring weeks (H/M)",
         "a lead fee on 100-300 zl queens is too small to matter (H/M)",
         "private breeders on OLX",
         "SEO on matka pszczela od reki phrases (V3-D08, 10 suggestions)",
         "[V3 #11](../findability/V3-hobby-niches.md#11-mated-buckfast-queen-available-now-od-ręki-v3-d08), [V3 scan 6](../research/verticals/V3-hobby-niches.md#6-hobbies-in-poland-size-and-supply-gap)"),
    65: ("no", "post-warranty smartwatch repair has no Polish brand (M/M)",
         "one partner technician is a single point of failure (H/M)",
         "one OLX technician (Lodz); iFixit parts abroad",
         "SEO on naprawa zegarka Garmin / Huawei phrases (V4-D01, 10 suggestions)",
         "[V4 #1](../findability/V4-services-with-logistics.md#1-garmin-watch-repair-v4-d01), [V4 #2](../findability/V4-services-with-logistics.md#2-battery-replacement-huawei-watch-gt-2-v4-d01)"),
    67: ("partly: care services repeat (Clothes Doctor 3-4 orders a year abroad)",
         "no Polish down-jacket repair found at all (M/H)",
         "no tailor with down-filling skills agrees to partner (M/H)",
         "unverified (no partner tailor named)",
         "SEO on naprawa kurtki puchowej (V4-D03, 10 suggestions)",
         "[V4 #4](../findability/V4-services-with-logistics.md#4-down-jacket-repair--refill-v4-d03), [V4 scan 4](../research/verticals/V4-services-with-logistics.md#4-what-the-numbers-say)"),
    69: ("no", "post-warranty owners of expensive robots prefer repair to replacement (M/M)",
         "maker services and dysonserwis.pl already take repairs (H/M)",
         "dysonserwis.pl and maker services; independent technicians unverified",
         "SEO on naprawa Roborock po gwarancji (V4-D05, 5 suggestions)",
         "[V4 #6](../findability/V4-services-with-logistics.md#6-roborock-repair-after-warranty-v4-d05), [V4 #7](../findability/V4-services-with-logistics.md#7-dyson-v15-repair-v4-d06)"),
    72: ("no", "foreign-only service means Polish owners pay heavy shipping today (M/M)",
         "no Polish electronics repairer takes the modules (M/H)",
         "UK and US module repair services (no Polish repairer found)",
         "SEO on naprawa wzmacniacza Bose phrases (V4-D09, 10 suggestions)",
         "[V4 #10](../findability/V4-services-with-logistics.md#10-car-premium-audio-amplifier-repair-bose-in-audi-a6-c6-v4-d09)"),
    81: ("partly: kitchens reorder gaskets and wear parts",
         "downtime makes restaurants pay a premium for a fast part (M/H)",
         "EU distributors do not sell to a newcomer reseller (M/H)",
         "Nisbets (IE) or Parts Town (US) seen in T10; EU distributor terms unverified",
         "SEO on uszczelka Unox and Carpigiani czesci phrases (V5-D08, 2+3 suggestions)",
         "[V5 #8](../findability/V5-small-business-buying.md#8-door-gasket-unox-combi-oven-xevc-v5-d08), [V5 #9](../findability/V5-small-business-buying.md#9-spare-parts-carpigiani-soft-serve-machine-v5-d08)"),
    84: ("partly: sewing workshops replace hooks and wear parts often",
         "a regional cluster can be reached with few contacts (M/M)",
         "cluster is too small and buys from mechanics it already knows (M/H)",
         "unverified (no Juki parts distributor named)",
         "unverified (Lodz/Pabianice sewing workshops, not listed)",
         "[V5 #11](../findability/V5-small-business-buying.md#11-hook-juki-ddl-8700-industrial-sewing-machine-v5-d12)"),
    85: ("partly: workshops replace seals often", "photo and dimensions to profile is a real AI classification (M/M)",
         "seal orders are too small to pay for delivery (H/M)",
         "RS PL distributor (shaft seals)",
         "SEO on uszczelniacz hydrauliczny wymiar phrases (V5-D13, 10 suggestions)",
         "[V5 #12](../findability/V5-small-business-buying.md#12-hydraulic-rod-seal-40508-v5-d13)"),
    87: ("yes: restaurants order several times a week and suppliers pay monthly for clean orders",
         "no Choco-like ordering app found in Poland (M/H)",
         "wholesalers will not pay and ERP integration (Subiekt, Comarch) stalls (H/H)",
         "Polish food wholesalers (none named; unverified)",
         "unverified (direct sales to wholesalers)",
         "[V5 scan 7](../research/verticals/V5-small-business-buying.md#7-ten-most-promising-analogues-for-poland-quick-polish-check), [V5 scan 9](../research/verticals/V5-small-business-buying.md#9-takeaways-for-t09t11)"),
    91: ("partly: job shops' clients reorder parts", "marketplace margin near Xometry's 33% (M/H)",
         "quality disputes land on the founder as seller of record (M/H)",
         "unverified (5-10 laser-cutting shops, none named)",
         "SEO on ciecie laserem na wymiar wycena online (V5 scan 9)",
         "[V5 scan 4](../research/verticals/V5-small-business-buying.md#4-what-the-numbers-say), [V5 scan 9](../research/verticals/V5-small-business-buying.md#9-takeaways-for-t09t11)"),
}

REJECT_GROUPS = [
    ("KO", "Knock-out: needs stock, capital or heavy physical work (F3 = 1 or F8 = 1)"),
    ("REG", "Regulation knock-out (F7 = 1)"),
    ("INC", "Found easily or already served by an incumbent (T10 E, F1 or F6 = 1-2)"),
    ("MERGE8", "Merged into #8 (camper parts)"),
    ("MERGE24", "Merged into #24 (heat-pump and AC parts for installers)"),
    ("MERGE36", "Merged into #36 (diagnosis before the part)"),
    ("MERGE67", "Merged into #67 (clothing care by post)"),
    ("UNTESTED", "Not tested by T10 and no supplier or size to stand on"),
    ("LOW", "Weaker than the shortlist: low unit economics, incumbents nearby, or the founder cannot carry it"),
]


def weighted(scores):
    return sum(int(s) * w for s, w in zip(scores, WEIGHTS))


def band(scores, w, t10):
    f = [int(s) for s in scores]
    note = []
    if w < 2.8:
        b = 0
    elif w < 3.5:
        b = 1
    elif w < 4.2:
        b = 2
    else:
        b = 3
    if b >= 2:
        ok = (min(f[0], f[1], f[3]) >= 3 and sum(x >= 4 for x in (f[0], f[1], f[3])) >= 2
              and f[5] >= 3 and t10 != "not tested")
        if not ok:
            b = 1
            note.append("15-30% conditions not met")
    if f[5] == 1 or f[0] == 1:
        b = 0
        note.append("F1 or F6 = 1")
    if f[6] == 1:
        b = 0
        note.append("F7 = 1")
    names = ["<5%", "5-15%", "15-30%", ">30%"]
    note.append("quick; O/R not yet applied")
    return names[b], "; ".join(note)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for n, (name, v, owner, model, sc, t10, dec, reason) in IDEAS.items():
        assert len(sc) == 9, n
        w = weighted(sc)
        if dec == "S":
            for i, s in enumerate(sc):
                assert s in "12345", n
            assert sc[2] != "1" and sc[7] != "1", f"knock-out on shortlist: {n}"
            b, note = band(sc, w, t10)
            rec, opp, risk, sup, chan, ev = SHORT[n]
            rows.append([n, name, v, owner or "-", model, rec] + [int(s) for s in sc]
                        + [f"{w:.2f}", round(w + 1e-9, 1), b, note, t10, reason, opp, risk, sup, chan,
                           f"[#{n} in longlist]({SEC[v]}); {ev}"])
    rows.sort(key=lambda r: -float(r[15]))
    header = (["idea", "name", "vertical", "owner_area", "main_model", "recurring_why"]
              + [f"F{i}" for i in range(1, 10)]
              + ["weighted_exact", "weighted", "band", "band_note", "t10", "reason", "top_opportunity",
                 "top_risk", "first_supplier", "first_channel", "evidence"])
    with open(os.path.join(here, "shortlist.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        wr.writerow(["rank"] + header)
        for i, r in enumerate(rows, 1):
            wr.writerow([i] + r)
    print(f"shortlist rows: {len(rows)}")
    for r in rows:
        print(f"  #{r[0]:<3} {r[2]} {r[15]} {r[17]:<6} {r[1]}")
    # rejected list
    print()
    for key, title in REJECT_GROUPS:
        items = [(n, d) for n, d in IDEAS.items() if d[6] == key]
        if not items:
            continue
        print(f"### {title}\n")
        for n, (name, v, owner, model, sc, t10, dec, reason) in items:
            own = f" · owner area: {owner}" if owner else ""
            print(f"- **#{n} {name}** ({v}{own}; quick {weighted(sc):.1f}) · {reason} · 2026-11-06")
        print()
    total = len(rows) + sum(1 for d in IDEAS.values() if d[6] != "S")
    print(f"total ideas accounted for: {total}")


if __name__ == "__main__":
    main()
