import pandas as pd
data=pd.read_csv('Student_marks_list.csv')

def printToppers(data):
    m,b,e,p,c,h,f,s,t = 0,0,0,0,0,0,0,0,0
    mt,bt,et,pt,ct,ht,ft,st,tt = [],[],[],[],[],[],[],[],[]
    data['Total']=data.sum(axis=1,skipna=True)
    for i in data.index:
        if m<data['Maths'][i] :
            m=data['Maths'][i]
            mt.clear()
            mt.append(data['Name'][i])
        elif m==data['Maths'][i] :
            mt.append(data['Name'][i])
        if b<data['Biology'][i] :
            b=data['Biology'][i]
            bt.clear()
            bt.append(data['Name'][i])
        elif b==data['Biology'][i] :
            bt.append(data['Name'][i])
        if e<data['English'][i] :
            e=data['English'][i]
            et.clear()
            et.append(data['Name'][i])
        elif e==data['English'][i] :
            et.append(data['Name'][i])
        if p<data['Physics'][i] :
            p=data['Physics'][i]
            pt.clear()
            pt.append(data['Name'][i])
        elif p==data['Physics'][i] :
            pt.append(data['Name'][i])
        if c<data['Chemistry'][i] :
            c=data['Chemistry'][i]
            ct.clear()
            ct.append(data['Name'][i])
        elif c==data['Chemistry'][i] :
            ct.append(data['Name'][i])
        if h<data['Hindi'][i] :
            h=data['Hindi'][i]
            ht.clear()
            ht.append(data['Name'][i])
        elif h==data['Hindi'][i] :
            ht.append(data['Name'][i])
        tot=data['Total'][i]
        if f<tot:
            f=tot
            tt.clear()
            tt.extend(st)
            st.clear()
            st.extend(ft)
            ft.clear()
            ft.append(data["Name"][i])
        elif f==tot:
            ft.append(data['Name'][i])
        elif s<tot:
            s=tot
            tt.clear()
            tt.extend(st)
            st.clear()
            st.append(data["Name"][i])
        elif s==tot:
            st.append(data['Name'][i])
        elif t<tot:
            t=tot
            tt.clear()
            tt.append(data["Name"][i])
        elif t==tot:
            tt.append(data['Name'][i])
                
    print('Topper in Maths is ',end="")
    print(*mt,sep=', ',end=".\n")
    print('Topper in Biology is ',end="")
    print(*bt,sep=', ',end=".\n")
    print('Topper in English is ',end="")
    print(*et,sep=', ',end=".\n")
    print('Topper in Physics is ',end="")
    print(*pt,sep=', ',end=".\n")
    print('Topper in Chemistry is ',end="")
    print(*ct,sep=', ',end=".\n")
    print('Topper in Hindi is ',end="")
    print(*ht,sep=', ',end=".\n")
    print('Best students in the class are ',end="")
    print(*ft,*st,*tt,sep=", ",end=".\n")

        
printToppers(data)