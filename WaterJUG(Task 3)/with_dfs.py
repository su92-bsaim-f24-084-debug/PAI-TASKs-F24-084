def solve(x_cap, y_cap, g):
    s = (0, 0)
    v = []
    stack = []
    stack.append((s, [(s, "Start: dono jugs khali hain")]))

    while stack:
        current_state, path = stack.pop()
        x = current_state[0]
        y = current_state[1]
        if x == g or y == g:
            print("\nGoal mil gaya!", g)
            print("Total steps:", len(path) - 1)
            step = 0
            for item in path:
                state = item[0]
                rule = item[1]
                print("Rule:", rule)
                print("State:",state)
                step +=1
            return
        if current_state in v:
            continue
        v.append(current_state)

        # ab saare possible moves try karenge (8 rules)

        # x ko fill kiya
        new_x = x_cap
        new_y = y
        if (new_x, new_y) not in v:
            new_state = (new_x, new_y)
            new_path = path + [(new_state, "1,jug X fill kiya")]
            stack.append((new_state, new_path))

        #y ko fill kiya
        new_x = x
        new_y = y_cap
        if (new_x, new_y) not in v:
            new_state = (new_x, new_y)
            new_path= path +[(new_state,"2,Jug Y fill kiy")]
            stack.append((new_state, new_path))
        # x khali
        new_x = 0
        new_y = y
        if (new_x, new_y) not in v:
            new_state= (new_x, new_y)
            new_path =path + [(new_state,"3,Jug X khali kiya")]
            stack.append((new_state, new_path))
        # y khali
        new_x = x
        new_y = 0
        if (new_x, new_y) not in v:
            new_state = (new_x, new_y)
            new_path = path + [(new_state,"4,Jug Y khali kiya")]
            stack.append((new_state, new_path))

        # rule 5 - x se y mein daalo jab tak x khali na ho jaye
        if x > 0 and y < y_cap:
            total = x + y
            if total <= y_cap:
                new_x = 0
                new_y = total
            else:
                new_x = total - y_cap
                new_y = y_cap
            if new_x == 0:
                if (new_x, new_y) not in v:
                    new_state = (new_x, new_y)
                    new_path = path + [(new_state, "5: X se Y mein daala, X khali ho gaya")]
                    stack.append((new_state, new_path))

        # rule 6 - x se y mein daalo jab tak y bhar na jaye
        if x > 0 and y < y_cap:
            total = x + y
            if total <= y_cap:
                new_x = 0
                new_y = total
            else:
                new_x = total - y_cap
                new_y = y_cap
            if new_y == y_cap:
                if (new_x, new_y) not in v:
                    new_state = (new_x, new_y)
                    new_path = path + [(new_state, "6: X se Y mein daala, Y bhar gaya")]
                    stack.append((new_state, new_path))

        # rule 7 - y se x mein daalo jab tak y khali na ho jaye
        if y > 0 and x < x_cap:
            total = x + y
            if total <= x_cap:
                new_x = total
                new_y = 0
            else:
                new_x = x_cap
                new_y = total - x_cap
            if new_y == 0:
                if (new_x, new_y) not in v:
                    new_state = (new_x, new_y)
                    new_path = path + [(new_state, "7: Y se X mein daala, Y khali ho gaya")]
                    stack.append((new_state, new_path))


        if y > 0 and x < x_cap:
            total = x + y
            if total <= x_cap:
                new_x = total
                new_y = 0
            else:
                new_x = x_cap
                new_y = total - x_cap
            if new_x == x_cap:
                if (new_x, new_y) not in v:
                    new_state = (new_x, new_y)
                    new_path = path + [(new_state, "8: Y se X mein daala, X bhar gaya")]
                    stack.append((new_state, new_path))


    print("\nKoi solution nahi mila :(")
    print("Goal", g, "liters achieve nahi ho sakta")
print("water_jug Problem")
x_capacity = int(input("Jug X ki capacity enter karo: "))
y_capacity = int(input("Jug Y ki capacity enter karo: "))
goal_amount = int(input("Goal: "))

solve(x_capacity, y_capacity, goal_amount)