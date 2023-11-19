from template.buildings import Buildings,Pmg,Pm


buildings = Buildings("buildings_explosives_building_chemical_plants",if_init=True)

m_pmg = Pmg("pmg_explosives_building_chemical_plants",if_init=True,Bindings=buildings)

print(buildings.data)
buildings.output("output/buildings.txt")
m_pmg.output("output/pmg.txt")




