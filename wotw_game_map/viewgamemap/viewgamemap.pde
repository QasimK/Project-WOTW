ArrayList view_list = new ArrayList();
ArrayList action_list = new ArrayList();

void setup() {
  size(1200, 600);
  
  String[] lines = loadStrings("game_map.txt");
  
  String curline = "";
  String current_action_name = "";
  Action current_action = null;;
  String current_parse = "";
  for(int i=0; i <lines.length; ++i) {
    //Parse the game_map.txt and create the objects
    curline = lines[i];
    println(curline);
    
    if(curline.length() == 0) {
      continue;
    }
    if(curline.length() >= 2 && curline.substring(0, 2).equals("a_")) {
      println("-Identify new action start");
      current_action_name = curline;
      current_action = null;
      current_parse = "";
      boolean notin = true;
      
      for(int ii=0; ii < action_list.size(); ii++) {
        Action actionobj = (Action) action_list.get(ii);
        if (actionobj.name.equals(current_action_name)) {
          notin = false;
          current_action = actionobj;
          break;
        }
      }
      if (notin) {
        Action newaction = new Action(current_action_name);
        action_list.add(newaction);
        current_action = newaction;
      }
    } else if (curline.equals("Views Required:")) {
      println("-Change state to view required");
      current_parse = "Views Required:";
    } else if (curline.equals("Views Allowed on Exit:")) {
      println("-Change state to allowed views on exit");
      current_parse = "Views Allowed on Exit:";
    } else {
      println("Add this view to the appropriate list");
      //curline should be the name of a view
      View viewobj = null;
      
      boolean notin = true;
      for(int ii=0; ii < view_list.size(); ii++) {
        viewobj = (View) view_list.get(ii);
        if(viewobj.name.equals(curline)) {
          notin = false;
          break;
        }
      }
      if(notin)  {
        viewobj = new View(curline);
        view_list.add(viewobj);
      }
      
      //Now add to appropriate action
      if(current_parse.equals("Views Required:")) {
        current_action.add_view_required(viewobj);
      } else if(current_parse.equals("Views Allowed on Exit:")) {
        current_action.add_allowed_exit_view(viewobj);
      } else {
        println("ERRROR");
        println("ERRROR");
        println("ERRROR");
      }
    }
  }
  
  println("::View List:");
  for(int i=0; i < view_list.size(); i++) {
    println(((View) view_list.get(i)).name);
  }
  println("");
  
  println("::Action List:\n");
  for(int i=0; i < action_list.size(); i++) {
    Action action = (Action) action_list.get(i);
    println(action.name);
    
    View viewobj;
    
    println("-Required Views:");
    ArrayList rv = action.required_views;
    for(int j=0; j < rv.size(); j++) {
      viewobj = (View) rv.get(j);
      println(viewobj.name);
    }
    
    println("-Allowed Exit Views:");
    ArrayList aev = action.allowed_exit_views;
    for(int j=0; j < aev.size(); j++) {
      viewobj = (View) aev.get(j);
      println(viewobj.name);
    }
    println("");
  }
}

void draw() {
  background(196, 196, 196);
}

class Action {
  String name;
  ArrayList required_views;
  ArrayList allowed_exit_views;
  
  Action(String tempname) {
    name = tempname;
    required_views = new ArrayList();
    allowed_exit_views = new ArrayList();
  }
  
  void add_view_required(View viewobj) {
    required_views.add(viewobj);
  }
  void add_allowed_exit_view(View viewobj) {
    allowed_exit_views.add(viewobj);
  }
}

class View {
  String name;
  
  View(String tempname) {
    name = tempname;
  }
}
