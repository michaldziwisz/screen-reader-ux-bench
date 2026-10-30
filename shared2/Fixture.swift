import Foundation
let fixture = try! JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments.contains("--fixture-bundle") ? Bundle.main.path(forResource:"fixture",ofType:"json")! : "shared2/fixture.json"))) as! [String:Any]
let records = fixture["records"] as! [[String:String]]
let detailsText = fixture["details"] as! String
