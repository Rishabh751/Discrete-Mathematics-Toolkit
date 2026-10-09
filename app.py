import streamlit as st
import sympy as sp
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import re
from itertools import product

st.set_page_config(page_title='Discrete Mathematics Toolkit', page_icon='📐', layout='wide')

def parse_set(text):
    text = text.strip().strip('{}')
    if not text: return set()
    out=set()
    for x in text.split(','):
        x=x.strip()
        if not x: continue
        try: out.add(int(x))
        except ValueError:
            try: out.add(float(x))
            except ValueError: out.add(x)
    return out

def relation_pairs(text):
    pairs=re.findall(r'\(([^,()]+),([^,()]+)\)', text.replace(' ',''))
    def cv(x):
        try: return int(x)
        except ValueError:
            try: return float(x)
            except ValueError: return x
    return {(cv(a),cv(b)) for a,b in pairs}

def logic_norm(s):
    s=s.strip()
    for pat,repl in [(r'\bAND\b','&'),(r'\bOR\b','|'),(r'\bNOT\b','~')]:
        s=re.sub(pat,repl,s,flags=re.I)
    return s.replace('¬','~').replace('∧','&').replace('∨','|')

def symbols_in(s):
    return sorted(set(re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b',s))-{'AND','OR','NOT'})

def parse_bool_expr(s):
    n=logic_norm(s)
    syms={x:sp.Symbol(x) for x in symbols_in(s)}
    return sp.sympify(n, locals=syms), list(syms)

def truth_table(expr):
    e,names=parse_bool_expr(expr)
    rows=[]
    syms={x:sp.Symbol(x) for x in names}
    for vals in product([False,True], repeat=len(names)):
        a=dict(zip([syms[x] for x in names],vals))
        rows.append({**{x:int(v) for x,v in zip(names,vals)},'Result':int(bool(e.subs(a)))})
    return pd.DataFrame(rows),e

def parse_edges(text, weighted=False):
    out=[]
    for line in text.splitlines():
        p=[x.strip() for x in line.split(',')]
        if not line.strip(): continue
        if weighted:
            if len(p)!=3: raise ValueError('Weighted edge must be A,B,weight')
            out.append((p[0],p[1],float(p[2])))
        else:
            if len(p)!=2: raise ValueError('Edge must be A,B')
            out.append((p[0],p[1]))
    return out

def draw_graph(G,title,highlight=None,node_colors=None):
    fig,ax=plt.subplots(figsize=(8,5)); pos=nx.spring_layout(G,seed=42)
    nx.draw_networkx_nodes(G,pos,node_color=node_colors or 'skyblue',node_size=850,ax=ax)
    nx.draw_networkx_labels(G,pos,font_weight='bold',ax=ax)
    nx.draw_networkx_edges(G,pos,width=2,ax=ax)
    if highlight:
        nx.draw_networkx_edges(G,pos,edgelist=list(highlight),width=4,edge_color='red',ax=ax)
    labels=nx.get_edge_attributes(G,'weight')
    if labels: nx.draw_networkx_edge_labels(G,pos,edge_labels=labels,ax=ax)
    ax.set_title(title); ax.axis('off'); return fig

st.sidebar.title('📚 Modules')
module=st.sidebar.radio('Choose a module',[
    '🏠 Home','🧠 Logic & Predicate Calculus','🔢 Sets & Relations',
    '🔷 Boolean Algebra','🕸️ Graph Theory','🌳 Trees & MST','🎨 Graph Coloring'])

if module=='🏠 Home':
    st.title('📐 Discrete Mathematics Toolkit')
    st.subheader('Interactive Problem Solver & Visualizer')
    st.write('A practical application for exploring major concepts from Discrete Mathematics.')
    cols=st.columns(3)
    cards=[
        ('🧠 Logic','Truth tables, tautology, contradiction and equivalence.'),
        ('🔢 Sets','Set operations, Venn-style analysis and relations.'),
        ('🔷 Boolean Algebra','Boolean expressions and simplification.'),
        ('🕸️ Graphs','Graph construction, degree and adjacency matrix.'),
        ('🌳 Trees & MST','Minimum spanning tree analysis.'),
        ('🎨 Coloring','Graph coloring and exam timetable scheduling.')]
    for i,(h,d) in enumerate(cards):
        with cols[i%3]: st.info(f'**{h}**\n\n{d}')
    st.divider(); st.header('🎯 Course Mapping')
    st.dataframe(pd.DataFrame({
        'CO':['CO1','CO2','CO3','CO4','CO5'],
        'Module':['Logic & Predicate Calculus','Sets & Relations','Boolean Algebra','Graph Theory','Trees, MST & Graph Coloring'],
        'Concepts':['Connectives, equivalence, inference, quantifiers','Relations, equivalence, partial order','Boolean functions, normal forms, switching','Paths, cycles, matrices, connectivity','Trees, cut sets, MST, chromatic number']}),use_container_width=True,hide_index=True)

elif module=='🧠 Logic & Predicate Calculus':
    st.title('🧠 Logic & Predicate Calculus')
    t1,t2,t3=st.tabs(['Truth Table','Equivalence','Inference Helper'])
    with t1:
        expr=st.text_input('Expression','(P AND Q) OR NOT P')
        if st.button('Generate Truth Table'):
            try:
                df,e=truth_table(expr); st.code(str(e)); st.dataframe(df,use_container_width=True,hide_index=True)
                r=df.Result.tolist()
                if all(x==1 for x in r): st.success('TAUTOLOGY')
                elif all(x==0 for x in r): st.error('CONTRADICTION')
                else: st.warning('CONTINGENCY')
            except Exception as ex: st.error(f'Could not parse expression: {ex}')
    with t2:
        a=st.text_input('Expression 1','P AND Q'); b=st.text_input('Expression 2','Q AND P')
        if st.button('Check Equivalence'):
            try:
                e1,n1=parse_bool_expr(a); e2,n2=parse_bool_expr(b); names=sorted(set(n1+n2)); syms={x:sp.Symbol(x) for x in names}
                ok=True; rows=[]
                for vals in product([False,True],repeat=len(names)):
                    ass=dict(zip([syms[x] for x in names],vals)); r1=int(bool(e1.subs(ass))); r2=int(bool(e2.subs(ass))); ok &= r1==r2
                    rows.append({**{x:int(v) for x,v in zip(names,vals)},'Expr 1':r1,'Expr 2':r2})
                st.success('✓ Logically equivalent' if ok else '✗ Not logically equivalent'); st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            except Exception as ex: st.error(f'Could not compare: {ex}')
    with t3:
        st.write('Try a common pattern such as Modus Ponens: P → Q, P ⟹ Q.')
        premises=st.text_area('Premises (one per line)','P → Q\nP'); conclusion=st.text_input('Conclusion','Q')
        if st.button('Analyze Inference'):
            p=[logic_norm(x).replace('→','>>').strip() for x in premises.splitlines() if x.strip()]; c=logic_norm(conclusion).strip(); found=[]
            if len(p)>=2 and '>>' in p[0]:
                left,right=[x.strip() for x in p[0].split('>>',1)]
                if p[1]==left and c==right: found.append('Modus Ponens')
                if p[1] in ('~'+right,'~('+right+')') and c=='~'+left: found.append('Modus Tollens')
            st.success('Detected: '+', '.join(found)) if found else st.info('No supported basic pattern detected.')

elif module=='🔢 Sets & Relations':
    st.title('🔢 Sets & Relations'); t1,t2=st.tabs(['Set Operations','Relations'])
    with t1:
        c1,c2,c3=st.columns(3)
        with c1: A=parse_set(st.text_input('Set A','{1,2,3,4}'))
        with c2: B=parse_set(st.text_input('Set B','{3,4,5,6}'))
        with c3: U=parse_set(st.text_input('Universal Set U','{1,2,3,4,5,6,7,8}'))
        def sv(x): return sorted(x,key=str)
        res={'A ∪ B':sv(A|B),'A ∩ B':sv(A&B),'A − B':sv(A-B),'B − A':sv(B-A),'A′':sv(U-A),'B′':sv(U-B),'A △ B':sv(A^B)}
        st.dataframe(pd.DataFrame([{'Operation':k,'Result':str(v)} for k,v in res.items()]),use_container_width=True,hide_index=True)
        fig,ax=plt.subplots(figsize=(7,4)); ax.set_xlim(0,10); ax.set_ylim(0,6)
        ax.add_patch(plt.Circle((4,3),2,fill=False,linewidth=2)); ax.add_patch(plt.Circle((6,3),2,fill=False,linewidth=2))
        ax.text(3,5.2,'A',fontsize=14); ax.text(6.7,5.2,'B',fontsize=14); ax.text(5,3,f'|A∩B|={len(A&B)}',ha='center'); ax.axis('off'); st.pyplot(fig)
    with t2:
        A=parse_set(st.text_input('Base set A','{1,2,3}')); R=relation_pairs(st.text_input('Relation R','{(1,1),(2,2),(3,3),(1,2),(2,1)}'))
        if st.button('Analyze Relation'):
            ref=all((a,a) in R for a in A); sym=all((b,a) in R for a,b in R); anti=all(a==b or (b,a) not in R for a,b in R)
            trans=all((a,c) in R for a,b in R for c,d in R if b==c)
            st.dataframe(pd.DataFrame({'Property':['Reflexive','Symmetric','Antisymmetric','Transitive'],'Result':[ref,sym,anti,trans]}),use_container_width=True,hide_index=True)
            if ref and sym and trans: st.success('✓ Equivalence relation')
            if ref and anti and trans: st.success('✓ Partial-order relation')

elif module=='🔷 Boolean Algebra':
    st.title('🔷 Boolean Algebra')
    expr=st.text_input('Boolean expression','A AND B OR A AND NOT B')
    if st.button('Analyze Boolean Expression'):
        try:
            df,e=truth_table(expr); st.dataframe(df,use_container_width=True,hide_index=True); st.subheader('Simplified Expression'); st.code(str(sp.simplify_logic(e,form='dnf')))
        except Exception as ex: st.error(f'Could not simplify: {ex}')
    st.divider(); st.subheader('📘 Common Boolean Laws')
    st.dataframe(pd.DataFrame({'Law':['Identity','Domination','Idempotent','Complement','Double Negation','De Morgan'],'Expression':['A + 0 = A, A·1 = A','A + 1 = 1, A·0 = 0','A + A = A, A·A = A','A + A′ = 1, A·A′ = 0','(A′)′ = A','(A+B)′ = A′·B′']}),use_container_width=True,hide_index=True)

elif module=='🕸️ Graph Theory':
    st.title('🕸️ Graph Theory')
    text=st.text_area('Edges (one per line as A,B)','A,B\nA,C\nB,D\nC,D\nD,E')
    if st.button('Build Graph'):
        try:
            G=nx.Graph(); G.add_edges_from(parse_edges(text)); st.pyplot(draw_graph(G,'Input Graph'))
            c1,c2=st.columns(2)
            with c1:
                st.write('Vertices:',list(G.nodes())); st.write('Edges:',list(G.edges())); st.write('Number of vertices:',G.number_of_nodes()); st.write('Number of edges:',G.number_of_edges()); st.write('Connected:',nx.is_connected(G) if G.number_of_nodes() else False); st.write('Degree sequence:',sorted(dict(G.degree()).values(),reverse=True))
            with c2:
                nodes=list(G.nodes()); M=nx.to_numpy_array(G,nodelist=nodes,dtype=int); st.dataframe(pd.DataFrame(M,index=nodes,columns=nodes),use_container_width=True)
            st.success('✓ Bipartite graph') if nx.is_bipartite(G) else st.warning('Not bipartite')
            st.success('✓ Eulerian graph') if nx.is_eulerian(G) else st.info('Not Eulerian')
        except Exception as ex: st.error(f'Could not build graph: {ex}')

elif module=='🌳 Trees & MST':
    st.title('🌳 Trees & Minimum Spanning Tree')
    text=st.text_area('Weighted edges (A,B,weight)','A,B,4\nA,C,2\nB,C,5\nB,D,3\nC,D,1\nC,E,6\nD,E,2')
    algo=st.selectbox('Algorithm',['Kruskal’s Algorithm','Prim’s Algorithm'])
    if st.button('Find Minimum Spanning Tree'):
        try:
            G=nx.Graph(); G.add_weighted_edges_from(parse_edges(text,True))
            if not nx.is_connected(G): st.error('Graph must be connected.')
            else:
                mst=nx.minimum_spanning_tree(G); st.success(f"MST total cost = {mst.size(weight='weight'):g}"); st.pyplot(draw_graph(G,'MST Highlighted',mst.edges()))
                rows=[]
                for u,v,d in sorted(G.edges(data=True),key=lambda x:x[2]['weight']): rows.append({'Edge':f'{u} — {v}','Weight':d['weight'],'Selected':'✓' if mst.has_edge(u,v) else '✗'})
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                st.caption('Kruskal: choose lightest safe edges. Prim: grow the tree from a starting vertex. The current implementation computes the MST and visualizes the selected edges.')
        except Exception as ex: st.error(f'Could not compute MST: {ex}')

elif module=='🎨 Graph Coloring':
    st.title('🎨 Graph Coloring & Exam Timetable')
    text=st.text_area('Conflicts (one per line as Subject1,Subject2)','Math,Physics\nMath,DSA\nPhysics,DBMS\nDSA,DBMS\nDBMS,OS\nDSA,OS\nOS,Networks')
    if st.button('Color Graph'):
        try:
            G=nx.Graph(); G.add_edges_from(parse_edges(text)); coloring=nx.coloring.greedy_color(G,strategy='saturation_largest_first'); k=max(coloring.values(),default=-1)+1
            palette=['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
            colors=[palette[coloring[n]%len(palette)] for n in G.nodes()]
            st.success(f'Valid coloring found using {k} color(s).'); st.pyplot(draw_graph(G,f'Graph Coloring — {k} colors',node_colors=colors))
            rows=[{'Subject / Vertex':n,'Color':coloring[n]+1,'Exam Slot':f'Slot {coloring[n]+1}'} for n in sorted(G,key=str)]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); st.info(f'The generated timetable uses {k} slots for this coloring. The greedy algorithm is a practical heuristic; exact chromatic-number calculation is a future upgrade.')
        except Exception as ex: st.error(f'Could not color graph: {ex}')

st.sidebar.divider(); st.sidebar.caption('Discrete Mathematics Toolkit • Version 1.0')
