from template.buildings import Buildings,Pmg,Pm


buildings = Buildings("buildings_explosives_building_chemical_plants",if_init=False)

m_pmg = Pmg("pmg_explosives_building_chemical_plants",if_init=True,Bindings=buildings)

buildings.add("severity", "=", "fail","possible.error_check",if_recursive=True)
print(buildings.data)
buildings.add("unique", "=", "yes")
buildings.output("output/buildings.txt")

m_pmg.output("output/pmg.txt")




