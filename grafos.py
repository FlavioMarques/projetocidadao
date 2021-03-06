from streamlit_agraph import agraph, Node, Edge, Config

nodes = []
edges = []
nodes.append( Node(id="Spiderman", label="Peter Parker", size=400, svg="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png") ) # includes **kwargs
nodes.append( Node(id="Captain_Marvel", size=400, svg="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png") )
edges.append( Edge(source="Captain_Marvel", label="friend_of", target="Spiderman", type="CURVE_SMOOTH") ) # includes **kwargs

config = Config(width=500,
                height=500,
                directed=True,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6", # or "blue"
                collapsible=True,
                node={'labelProperty':'label'},
                link={'labelProperty': 'label', 'renderLabel': True}
                # **kwargs e.g. node_size=1000 or node_color="blue"
                )

return_value = agraph(nodes=nodes,
                      edges=edges,
                      config=config)

